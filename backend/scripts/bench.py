#!/usr/bin/env python
"""Bench reproductible des endpoints sensibles aux performances.

Seed une base jetable (user + decks + cartes + sessions), puis mesure pour
chaque endpoint la latence et le NOMBRE DE REQUÊTES SQL (détecteur de N+1).

Usage :
    cd backend && python scripts/bench.py                 # SQLite jetable
    cd backend && python scripts/bench.py --decks 80 --cards 300
    DATABASE_URL=postgresql://user:pass@localhost/bench \\
        python scripts/bench.py                            # bench sur PostgreSQL
"""
import argparse
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decks", type=int, default=50)
    parser.add_argument("--cards", type=int, default=200, help="cartes par deck")
    parser.add_argument("--repeat", type=int, default=5, help="mesures par endpoint")
    args = parser.parse_args()

    os.environ.setdefault("FLASK_ENV", "development")

    from app import create_app
    from app.extensions import db
    from app.models.user import User
    from app.models.deck import Deck
    from app.models.flashcard import Flashcard
    from app.models.study_session import StudySession
    from app.utils.sql_profiler import _query_counter
    from datetime import datetime, timedelta

    app = create_app("development")
    if not os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/studyhub_bench.db"
    app.config["RATELIMIT_ENABLED"] = False

    print(f"DB = {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Seed : {args.decks} decks x {args.cards} cartes ...")

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(email="bench@example.com", username="bench")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        now = datetime.utcnow()
        for d in range(args.decks):
            deck = Deck(name=f"Deck {d}", user_id=user.id)
            db.session.add(deck)
            db.session.flush()
            db.session.bulk_save_objects([
                Flashcard(deck_id=deck.id, front=f"Q{i}", back=f"A{i}",
                          next_review=now - timedelta(days=1))
                for i in range(args.cards)
            ])
        # Quelques sessions d'étude pour heatmap/overview
        db.session.bulk_save_objects([
            StudySession(user_id=user.id, module="flashcard", duration_seconds=60,
                         cards_reviewed=10, cards_correct=8,
                         created_at=now - timedelta(days=i))
            for i in range(60)
        ])
        db.session.commit()

    client = app.test_client()
    login = client.post("/api/v1/auth/login",
                        json={"email": "bench@example.com", "password": "password123"})
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        ("GET", "/api/v1/decks?per_page=20"),
        ("GET", "/api/v1/stats/overview"),
        ("GET", "/api/v1/stats/heatmap"),
        ("GET", "/api/v1/notes?per_page=20"),
    ]

    print(f"\n{'endpoint':<40} {'latence (ms)':>14} {'requêtes SQL':>14}")
    print("-" * 70)
    for method, path in endpoints:
        durations, queries = [], 0
        for _ in range(args.repeat):
            start_count = _query_counter.get()
            t0 = time.perf_counter()
            resp = client.open(path, method=method, headers=headers)
            durations.append((time.perf_counter() - t0) * 1000)
            queries = _query_counter.get() - start_count
            status = resp.status_code
        median = statistics.median(durations)
        flag = "  <-- N+1 ?" if queries > 10 else ""
        print(f"{path:<40} {median:>14.1f} {queries:>14}{flag}  [{status}]")


if __name__ == "__main__":
    main()
