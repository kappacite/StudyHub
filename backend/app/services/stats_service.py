from datetime import datetime, timedelta, date
from typing import List, Optional
from sqlalchemy import func
from app.dao.study_session_dao import StudySessionDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.models.study_session import StudySession
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.schemas.stats_schema import (
    StudySessionCreate, StudySessionResponse, StatsOverviewResponse, 
    HeatmapItem, DeckStatsResponse, DashboardStatsResponse, DashboardKpis
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class StatsService:
    def __init__(
        self, 
        study_session_dao: StudySessionDAO, 
        deck_dao: DeckDAO,
        flashcard_dao: FlashcardDAO
    ):
        self._study_session_dao = study_session_dao
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao

    def create_session(self, user_id: int, data: StudySessionCreate) -> StudySessionResponse:
        session = StudySession(
            user_id=user_id,
            module=data.module,
            duration_seconds=data.duration_seconds,
            cards_reviewed=data.cards_reviewed,
            cards_correct=data.cards_correct
        )
        created = self._study_session_dao.create(session)
        
        # Enregistrement automatique de l'activité dans les groupes de l'utilisateur
        try:
            from app.dao.group_dao import GroupDAO
            from app.extensions import db
            group_dao = GroupDAO(db.session)
            user_groups = group_dao.get_user_groups(user_id)
            for group in user_groups:
                group_dao.add_group_activity(
                    group_id=group.id,
                    user_id=user_id,
                    activity_type="completed_session",
                    payload={
                        "module": data.module,
                        "duration_seconds": data.duration_seconds,
                        "cards_reviewed": data.cards_reviewed,
                        "cards_correct": data.cards_correct
                    }
                )
        except Exception as e:
            # Ne pas bloquer la création de session si l'enregistrement de l'activité échoue
            pass

        return StudySessionResponse.model_validate(created)

    def get_sessions(
        self, 
        user_id: int, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None, 
        module: Optional[str] = None
    ) -> List[StudySessionResponse]:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        sessions = self._study_session_dao.get_sessions(user_id, start_dt, end_dt, module)
        return [StudySessionResponse.model_validate(s) for s in sessions]

    def get_overview(self, user_id: int) -> StatsOverviewResponse:
        total_time = self._study_session_dao.get_total_duration(user_id)
        cards_stats = self._study_session_dao.get_cards_reviewed_stats(user_id)
        
        # Calcul du streak
        streak = self._calculate_streak(user_id)
        
        return StatsOverviewResponse(
            streak=streak,
            total_time_seconds=total_time,
            total_reviewed=cards_stats["total_reviewed"],
            total_correct=cards_stats["total_correct"]
        )

    def get_heatmap(self, user_id: int) -> List[HeatmapItem]:
        # 365 derniers jours
        start_date = datetime.utcnow() - timedelta(days=365)
        data = self._study_session_dao.get_heatmap_data(user_id, start_date)
        return [HeatmapItem(date=d["date"], duration=d["duration"], count=d["count"]) for d in data]

    def get_deck_stats(self, user_id: int, deck_id: int) -> DeckStatsResponse:
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce deck.")
            
        cards = deck.cards
        total_cards = len(cards)
        
        if total_cards == 0:
            return DeckStatsResponse(
                deck_id=deck_id,
                retention_rate=0.0,
                next_review=None,
                cards_to_review=0,
                total_cards=0
            )
            
        # Calcul du taux de rétention : ratio de cartes apprises avec succès (repetitions > 0)
        # ou cartes dont la prochaine révision est dans le futur
        now = datetime.utcnow()
        cards_retained = sum(1 for c in cards if c.next_review > now)
        retention_rate = (cards_retained / total_cards) * 100.0
        
        # Prochain réveil (date minimale de révision)
        next_reviews = [c.next_review for c in cards]
        next_review_date = min(next_reviews) if next_reviews else None
        
        # Nombre de cartes à réviser aujourd'hui (next_review <= maintenant)
        cards_to_review = sum(1 for c in cards if c.next_review <= now)
        
        return DeckStatsResponse(
            deck_id=deck_id,
            retention_rate=round(retention_rate, 2),
            next_review=next_review_date,
            cards_to_review=cards_to_review,
            total_cards=total_cards
        )

    def _calculate_streak(self, user_id: int) -> int:
        # Récupérer les sessions d'étude des 365 derniers jours
        start_date = datetime.utcnow() - timedelta(days=365)
        sessions = self._study_session_dao.get_sessions(user_id, start_date=start_date)
        
        if not sessions:
            return 0
            
        # Extraire les dates uniques au format YYYY-MM-DD
        study_dates = {s.created_at.date() for s in sessions}
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Le streak continue s'il y a eu étude aujourd'hui ou hier
        if today not in study_dates and yesterday not in study_dates:
            return 0
            
        streak = 0
        current_date = today if today in study_dates else yesterday
        
        while current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
            
        return streak

    def get_dashboard_stats(self, user_id: int) -> DashboardStatsResponse:
        # 1. KPIs
        # Total de cartes étudiées (somme des cartes révisées)
        total_cards_studied = (
            self._study_session_dao.db.query(func.sum(StudySession.cards_reviewed))
            .filter(StudySession.user_id == user_id, StudySession.module == "flashcard")
            .scalar()
        ) or 0
        
        # Nombre de cartes matures (interval > 21)
        mature_cards = (
            self._flashcard_dao.db.query(func.count(Flashcard.id))
            .join(Deck)
            .filter(Deck.user_id == user_id, Flashcard.interval > 21)
            .scalar()
        ) or 0
        
        # Taux de rétention (mature_cards / total_cards_studied * 100)
        retention_rate = 0.0
        if total_cards_studied > 0:
            retention_rate = round((mature_cards / total_cards_studied) * 100.0, 2)
            
        kpis = DashboardKpis(
            total_cards_studied=total_cards_studied,
            mature_cards=mature_cards,
            retention_rate=retention_rate
        )
        
        # 2. Heatmap (365 derniers jours)
        start_date = datetime.utcnow() - timedelta(days=365)
        date_col = func.date(StudySession.created_at)
        heatmap_results = (
            self._study_session_dao.db.query(date_col, func.count(StudySession.id))
            .filter(StudySession.user_id == user_id, StudySession.created_at >= start_date)
            .group_by(date_col)
            .all()
        )
        
        heatmap_dict = {}
        for r in heatmap_results:
            if r[0]:
                date_str = r[0] if isinstance(r[0], str) else r[0].isoformat()
                heatmap_dict[date_str] = r[1]
                
        # 3. Maturity Distribution
        learning_cards = (
            self._flashcard_dao.db.query(func.count(Flashcard.id))
            .join(Deck)
            .filter(Deck.user_id == user_id, Flashcard.interval < 1)
            .scalar()
        ) or 0
        
        young_cards = (
            self._flashcard_dao.db.query(func.count(Flashcard.id))
            .join(Deck)
            .filter(Deck.user_id == user_id, Flashcard.interval >= 1, Flashcard.interval <= 21)
            .scalar()
        ) or 0
        
        maturity_dist = {
            "learning": learning_cards,
            "young": young_cards,
            "mature": mature_cards
        }
        
        # 4. Forecast 7 jours
        today = date.today()
        forecast_dict = {}
        
        # Initialiser les 7 jours avec 0
        for i in range(7):
            d = today + timedelta(days=i)
            forecast_dict[d.isoformat()] = 0
            
        next_review_date_col = func.date(Flashcard.next_review)
        forecast_results = (
            self._flashcard_dao.db.query(next_review_date_col, func.count(Flashcard.id))
            .join(Deck)
            .filter(
                Deck.user_id == user_id, 
                next_review_date_col >= today.isoformat(),
                next_review_date_col <= (today + timedelta(days=6)).isoformat()
            )
            .group_by(next_review_date_col)
            .all()
        )
        
        for r in forecast_results:
            if r[0]:
                date_str = r[0] if isinstance(r[0], str) else r[0].isoformat()
                if date_str in forecast_dict:
                    forecast_dict[date_str] = r[1]
                    
        return DashboardStatsResponse(
            kpi=kpis,
            heatmap=heatmap_dict,
            maturity_distribution=maturity_dist,
            forecast_7_days=forecast_dict
        )
