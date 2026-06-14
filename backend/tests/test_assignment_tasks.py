"""
Tests PR1 — Fondation « devoirs multi-tâches ».

Couvre :
  - la migration crée les nouvelles tables/colonnes ;
  - la migration backfill : un devoir mono-classeur existant devient une tâche flashcards ;
  - les modèles + AssignmentDAO (round-trip CRUD).
"""
from sqlalchemy import inspect, text


def _fresh_app(monkeypatch, tmp_path, name="a.db"):
    # DevelopmentConfig.SQLALCHEMY_DATABASE_URI est calculé à l'import (attribut de
    # classe) et figé par Flask-SQLAlchemy à l'init. On patche donc l'attribut de
    # classe AVANT create_app pour obtenir une base SQLite jetable réellement isolée.
    from app import create_app
    from app import config as config_module
    monkeypatch.setattr(
        config_module.DevelopmentConfig,
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{tmp_path / name}",
    )
    return create_app("development")


def test_migration_creates_new_tables_and_columns(monkeypatch, tmp_path):
    from app.db_migrate import run_auto_migrations
    from app.extensions import db

    app = _fresh_app(monkeypatch, tmp_path)
    run_auto_migrations(app)

    with app.app_context():
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        assert "assignment_tasks" in tables
        assert "assignment_task_progress" in tables

        asgn_cols = {c["name"] for c in insp.get_columns("assignments")}
        assert {"instructions", "publish_at", "allow_late"} <= asgn_cols
        # binder_id doit être devenu nullable
        binder_col = next(c for c in insp.get_columns("assignments") if c["name"] == "binder_id")
        assert binder_col["nullable"] is True


def test_migration_backfills_legacy_assignment_to_flashcards_task(monkeypatch, tmp_path):
    from flask_migrate import upgrade as alembic_upgrade
    from app.extensions import db

    app = _fresh_app(monkeypatch, tmp_path, name="backfill.db")
    with app.app_context():
        # 1) Migrer jusqu'au parent immédiat de la refonte (= schéma « avant »).
        alembic_upgrade(revision="a1c2e3f4b5d6")

        db.session.execute(text(
            "INSERT INTO users (email, username, password_hash, is_active) "
            "VALUES ('prof@t.co', 'prof', 'x', 1)"
        ))
        db.session.execute(text(
            "INSERT INTO binders (uuid, name, user_id, is_public, fork_count) "
            "VALUES ('uuid-bio', 'Biologie', 1, 0, 0)"
        ))
        db.session.execute(text(
            "INSERT INTO assignments (group_id, binder_id, title, created_by) "
            "VALUES (1, 1, 'Chapitre 1', 1)"
        ))
        db.session.commit()

        # 2) Appliquer la refonte multi-tâches (backfill).
        alembic_upgrade(revision="b7d1a2c3e4f5")

        rows = db.session.execute(text(
            'SELECT task_type, ref_id, ref_uuid, ref_label, "order" FROM assignment_tasks'
        )).fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "flashcards"
    assert rows[0][1] == 1            # ref_id = binder._id
    assert rows[0][2] == "uuid-bio"   # ref_uuid = binder.uuid
    assert rows[0][3] == "Biologie"   # ref_label = binder.name
    assert rows[0][4] == 0            # order


def test_assignment_dao_roundtrip(app):
    from app.extensions import db
    from app.models.user import User
    from app.models.group import Group
    from app.models.assignment import Assignment, AssignmentTask
    from app.dao.assignment_dao import AssignmentDAO

    with app.app_context():
        u = User(email="dao@t.co", username="daoprof")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()

        g = Group(name="Classe DAO", invite_code="DAOCODE1",
                  created_by=u.id, type="class", is_class=True)
        db.session.add(g)
        db.session.commit()

        dao = AssignmentDAO(db.session)

        asgn = dao.add_assignment(Assignment(group_id=g.id, title="Devoir DAO", created_by=u.id))
        assert asgn.id is not None
        # binder_id nullable : un devoir purement multi-tâches est permis
        assert asgn.binder_id is None

        task = dao.add_task(AssignmentTask(
            assignment_id=asgn.id, task_type="quiz", ref_id=42,
            ref_label="Note QCM", goal={"min_score": 80}, order=0,
        ))

        tp = dao.upsert_task_progress(task.id, u.id)
        tp.status = "done"
        tp.score_pct = 91.0
        db.session.commit()

        sub = dao.upsert_submission(asgn.id, u.id)
        assert sub.cards_reviewed == 0

        loaded = dao.get_assignment_with_tasks(asgn.id)
        assert len(loaded.tasks) == 1
        assert loaded.tasks[0].task_type == "quiz"
        assert loaded.tasks[0].goal["min_score"] == 80

        assert dao.get_task_progress(task.id, u.id).score_pct == 91.0
        assert len(dao.list_tasks(asgn.id)) == 1
        assert len(dao.list_submissions(asgn.id)) == 1
        assert len(dao.list_task_progress_for_user(asgn.id, u.id)) == 1
