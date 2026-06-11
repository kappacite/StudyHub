from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import func
from app.extensions import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.models.note import Note
from app.models.study_session import StudySession
from app.models.binder import Binder
from app.schemas.focus_schema import (
    FocusTodayResponse, FocusItemSchema,
    FocusForecastResponse, ForecastItemSchema,
    FocusRetentionResponse, RetentionSubjectSchema
)

class FocusService:
    def get_today_items(self, user_id: int) -> FocusTodayResponse:
        now = datetime.utcnow()
        today = now.date()
        one_day_ago = now - timedelta(days=1)
        
        # 1. Fetch due flashcards grouped by deck
        decks = db.session.query(Deck).filter(Deck.user_id == user_id).all()
        deck_items = []
        flashcard_count = 0
        total_late_cards = 0

        for deck in decks:
            # Count due cards in deck
            due_cards = (
                db.session.query(Flashcard)
                .filter(
                    Flashcard.deck_id == deck.id,
                    Flashcard.next_review <= now
                )
                .all()
            )
            
            count = len(due_cards)
            if count > 0:
                flashcard_count += count
                # Check if any due card is late (next_review < today - 1 day)
                is_late = any(c.next_review < one_day_ago for c in due_cards)
                if is_late:
                    total_late_cards += sum(1 for c in due_cards if c.next_review < one_day_ago)
                
                # Fetch last study session for this deck
                last_session_time = (
                    db.session.query(func.max(StudySession.created_at))
                    .join(Flashcard, StudySession.flashcard_id == Flashcard.id)
                    .filter(
                        StudySession.user_id == user_id,
                        StudySession.module == "flashcard",
                        Flashcard.deck_id == deck.id
                    )
                    .scalar()
                )
                
                last_session_ago_days = None
                if last_session_time:
                    last_session_ago_days = (now - last_session_time).days
                
                deck_items.append(FocusItemSchema(
                    type="deck",
                    id=deck.id,
                    title=deck.name,
                    count=count,
                    is_late=is_late,
                    last_session_ago_days=last_session_ago_days
                ))

        # 2. Fetch due notes for blurting
        notes = db.session.query(Note).filter(Note.user_id == user_id).all()
        note_items = []
        blurting_count = 0
        total_late_notes = 0

        for note in notes:
            is_due = False
            is_late = False
            last_session_ago_days = None

            if note.last_blurting_at is None:
                # Never blurted, so it's due
                is_due = True
                days_since_created = (now - note.created_at).days
                if days_since_created >= 8:
                    is_late = True
            else:
                days_since_last = (now - note.last_blurting_at).days
                last_session_ago_days = days_since_last
                if days_since_last >= 7:
                    is_due = True
                if days_since_last >= 8:
                    is_late = True

            if is_due:
                blurting_count += 1
                if is_late:
                    total_late_notes += 1
                
                note_items.append(FocusItemSchema(
                    type="note",
                    id=note.id,
                    title=note.title or "Note sans titre",
                    count=1,
                    is_late=is_late,
                    last_session_ago_days=last_session_ago_days
                ))

        items = deck_items + note_items
        # Sort items: late ones first
        items.sort(key=lambda x: (not x.is_late, x.title))

        # 3. Devoirs avec deadline ≤ 3 jours (Feature 10)
        assignment_items = []
        assignment_count = 0
        try:
            from app.services.class_service import ClassService
            from app.dao.group_dao import GroupDAO
            from app.dao.binder_dao import BinderDAO
            from app.dao.user_dao import UserDAO
            class_service = ClassService(
                group_dao=GroupDAO(db.session),
                binder_dao=BinderDAO(db.session),
                user_dao=UserDAO(db.session)
            )
            due_soon = class_service.get_assignments_due_soon(user_id, days=3)
            for asgn in due_soon:
                is_late = asgn.status == "late"
                assignment_items.append(FocusItemSchema(
                    type="assignment",
                    id=asgn.binder_id,
                    assignment_id=asgn.id,
                    title=f"{asgn.title} ({asgn.group_name})",
                    count=1,
                    is_late=is_late,
                    due_date=asgn.due_date.date().isoformat() if asgn.due_date else None
                ))
            assignment_count = len(assignment_items)
        except Exception:
            pass  # Ne pas bloquer le Focus si les classes ne sont pas disponibles

        all_items = assignment_items + items
        all_items.sort(key=lambda x: (not x.is_late, x.title))

        return FocusTodayResponse(
            total_due=flashcard_count + blurting_count + assignment_count,
            late_count=total_late_cards + total_late_notes,
            flashcard_count=flashcard_count,
            blurting_count=blurting_count,
            assignment_count=assignment_count,
            items=all_items
        )

    def get_forecast(self, user_id: int, days: int = 14) -> FocusForecastResponse:
        now = datetime.utcnow()
        today_date = now.date()
        
        forecast_dict = { (today_date + timedelta(days=i)).isoformat(): 0 for i in range(days) }

        # Query all flashcards of the user
        cards = db.session.query(Flashcard).join(Deck).filter(Deck.user_id == user_id).all()
        for c in cards:
            if c.next_review:
                card_date = c.next_review.date()
                date_str = card_date.isoformat()
                if date_str in forecast_dict:
                    forecast_dict[date_str] += 1

        forecast_list = []
        for date_str in sorted(forecast_dict.keys()):
            count = forecast_dict[date_str]
            if count < 10:
                level = "low"
            elif count <= 25:
                level = "medium"
            else:
                level = "high"
            
            forecast_list.append(ForecastItemSchema(
                date=date_str,
                count=count,
                load_level=level
            ))

        return FocusForecastResponse(forecast=forecast_list)

    def get_retention_by_subject(self, user_id: int) -> FocusRetentionResponse:
        now = datetime.utcnow()
        binders = db.session.query(Binder).filter(Binder.user_id == user_id).all()
        
        by_subject = []
        for binder in binders:
            # Query sessions in the last 30 days for this binder
            sessions_30d = (
                db.session.query(StudySession)
                .join(Flashcard, StudySession.flashcard_id == Flashcard.id)
                .join(Deck, Flashcard.deck_id == Deck.id)
                .filter(
                    Deck.binder_id == binder.id,
                    StudySession.user_id == user_id,
                    StudySession.module == "flashcard",
                    StudySession.created_at >= now - timedelta(days=30)
                )
                .all()
            )

            # Calculation of retention percentage (correct / reviewed)
            cards_reviewed_30d = sum(s.cards_reviewed for s in sessions_30d if s.cards_reviewed is not None)
            cards_correct_30d = sum(s.cards_correct for s in sessions_30d if s.cards_correct is not None)
            retention_pct = 0.0
            if cards_reviewed_30d > 0:
                retention_pct = round((cards_correct_30d / cards_reviewed_30d) * 100.0, 2)
            else:
                # Default to 100.0 if there has been no sessions yet (as a clean state)
                retention_pct = 100.0

            # Calculation of trend (rate over last 7 days vs rate 7-14 days ago)
            sessions_a = [s for s in sessions_30d if s.created_at >= now - timedelta(days=7)]
            sessions_b = [s for s in sessions_30d if now - timedelta(days=14) <= s.created_at < now - timedelta(days=7)]
            
            reviewed_a = sum(s.cards_reviewed for s in sessions_a if s.cards_reviewed is not None)
            correct_a = sum(s.cards_correct for s in sessions_a if s.cards_correct is not None)
            rate_a = (correct_a / reviewed_a * 100.0) if reviewed_a > 0 else 0.0
            
            reviewed_b = sum(s.cards_reviewed for s in sessions_b if s.cards_reviewed is not None)
            correct_b = sum(s.cards_correct for s in sessions_b if s.cards_correct is not None)
            rate_b = (correct_b / reviewed_b * 100.0) if reviewed_b > 0 else 0.0
            
            trend_7d = round(rate_a - rate_b, 2)

            # Overdue flashcards count in the binder
            overdue_count = (
                db.session.query(func.count(Flashcard.id))
                .join(Deck)
                .filter(
                    Deck.binder_id == binder.id,
                    Flashcard.next_review <= now
                )
                .scalar()
            ) or 0

            by_subject.append(RetentionSubjectSchema(
                binder_id=binder.id,
                binder_name=binder.name,
                retention_pct=retention_pct,
                overdue_count=overdue_count,
                trend_7d=trend_7d
            ))

        # Sort subjects by binder name
        by_subject.sort(key=lambda x: x.binder_name)
        return FocusRetentionResponse(by_subject=by_subject)
