import math
from datetime import datetime, timedelta
from typing import List, Optional
from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
from app.dao.study_session_dao import StudySessionDAO
from app.models.revision import RevisionSet, RevisionItem
from app.models.study_session import StudySession
from app.schemas.revision_schema import (
    RevisionItemStats, RevisionSetStats, RevisionHistoryPoint, RevisionItemSummary,
)


def item_label(set_type: str, payload: dict) -> str:
    """Libellé court d'un item selon son type (pour les listes de stats)."""
    payload = payload or {}
    raw = (
        payload.get("question") or payload.get("assertion")
        or payload.get("term") or payload.get("title") or ""
    )
    raw = str(raw).strip() or "(sans titre)"
    return raw[:80]
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

# Seuils (cf. D5).
MATURE_DAYS = 21          # un item est « mûr » quand son intervalle ≥ 21 jours (Anki)
LEECH_LAPSES = 4          # sangsue : échoué au moins 4 fois
TARGET_RETENTION = 85.0   # cible de rétention réelle (%)


def difficulty_from_ef(ease_factor: float) -> float:
    """Difficulté D ∈ [1,10] dérivée de l'ease factor SM-2 (EF bas ⇒ D haute)."""
    ef = min(2.5, max(1.3, ease_factor or 2.5))
    d = 1 + (2.5 - ef) / (2.5 - 1.3) * 9
    return round(d, 1)


def retrievability(interval: int, last_reviewed: Optional[datetime], now: datetime) -> float:
    """Récupérabilité R ∈ [0,1] via la courbe d'oubli d'Ebbinghaus R = exp(-t/S)."""
    if not last_reviewed or interval <= 0:
        return 0.0
    days = max(0.0, (now - last_reviewed).total_seconds() / 86400.0)
    r = math.exp(-days / interval)
    return round(min(1.0, max(0.0, r)), 2)


def project_mastery_date(interval: int, ease_factor: float, next_review: Optional[datetime],
                         now: datetime) -> Optional[datetime]:
    """Date de maîtrise estimée : projection SM-2 (réussites) jusqu'à interval ≥ MATURE_DAYS."""
    cur = max(1, interval)
    ef = max(1.3, ease_factor or 2.5)
    d = next_review or now
    for _ in range(20):
        if cur >= MATURE_DAYS:
            return d
        d = d + timedelta(days=cur)
        cur = int(round(cur * ef))
    return d


class RevisionStatsService:
    def __init__(self, set_dao: RevisionSetDAO, item_dao: RevisionItemDAO, session_dao: StudySessionDAO):
        self._set_dao = set_dao
        self._item_dao = item_dao
        self._session_dao = session_dao

    def _get_set_or_404(self, set_id: int, user_id: int) -> RevisionSet:
        rset = self._set_dao.get_by_id(set_id)
        if not rset:
            raise ResourceNotFoundError("Ensemble de révision introuvable.")
        if rset.user_id != user_id:
            if rset.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._set_dao.db, rset.binder_id, user_id, write_required=False)
            else:
                raise ForbiddenError("Accès interdit à cet ensemble.")
        return rset

    # --- Item -----------------------------------------------------------------

    def _compute_item_stats(self, item: RevisionItem, item_type: str,
                            sessions: List[StudySession], now: datetime) -> RevisionItemStats:
        graded = [s for s in sessions if s.grade is not None]
        reviews = len(graded)
        successes = sum(1 for s in graded if s.grade >= 3)
        lapses = sum(1 for s in graded if s.grade < 3)
        success_rate = round(successes / reviews * 100, 1) if reviews else 0.0
        last_reviewed = graded[-1].created_at if graded else None
        is_mature = item.interval >= MATURE_DAYS

        return RevisionItemStats(
            item_id=item.id,
            reviews=reviews,
            success_rate=success_rate,
            lapses=lapses,
            repetitions=item.repetitions,
            ease_factor=round(item.ease_factor, 2),
            interval=item.interval,
            next_review=item.next_review,
            last_reviewed=last_reviewed,
            stability_days=item.interval,
            difficulty=difficulty_from_ef(item.ease_factor),
            retrievability=retrievability(item.interval, last_reviewed, now),
            is_mature=is_mature,
            is_leech=lapses >= LEECH_LAPSES,
            mastered=is_mature,
            mastery_date=None if is_mature else project_mastery_date(item.interval, item.ease_factor, item.next_review, now),
            history=[RevisionHistoryPoint(date=s.created_at, grade=s.grade) for s in graded],
        )

    def get_item_stats(self, user_id: int, item_id: int) -> RevisionItemStats:
        item = self._item_dao.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError("Item de révision introuvable.")
        rset = self._get_set_or_404(item.set_id, user_id)
        sessions = self._session_dao.get_for_item(item.id, rset.type)
        return self._compute_item_stats(item, rset.type, sessions, datetime.utcnow())

    # --- Ensemble -------------------------------------------------------------

    def get_set_stats(self, user_id: int, set_id: int) -> RevisionSetStats:
        rset = self._get_set_or_404(set_id, user_id)
        now = datetime.utcnow()
        items = self._item_dao.get_by_set(set_id)
        item_ids = [i.id for i in items]

        # Une seule requête pour toutes les sessions de l'ensemble (anti-N+1).
        sessions = self._session_dao.get_for_items(item_ids, rset.type)
        by_item = {}
        for s in sessions:
            by_item.setdefault(s.item_id, []).append(s)

        items_count = len(items)
        reviewed_items = 0
        mastered_count = 0
        leeches_count = 0
        due_count = 0
        success_rates = []
        difficulties = []
        mature_reviews = 0
        mature_successes = 0
        item_summaries = []

        for item in items:
            graded = [s for s in by_item.get(item.id, []) if s.grade is not None]
            reviews = len(graded)
            successes = sum(1 for s in graded if s.grade >= 3)
            lapses = reviews - successes
            item_success = round(successes / reviews * 100, 1) if reviews else 0.0
            difficulty = difficulty_from_ef(item.ease_factor)
            is_mature = item.interval >= MATURE_DAYS
            is_leech = lapses >= LEECH_LAPSES
            is_due = bool(item.next_review and item.next_review <= now)
            last_reviewed = graded[-1].created_at if graded else None

            if reviews:
                reviewed_items += 1
                success_rates.append(item_success)
            difficulties.append(difficulty)
            if is_mature:
                mastered_count += 1
                mature_reviews += reviews
                mature_successes += successes
            if is_leech:
                leeches_count += 1
            if is_due:
                due_count += 1

            item_summaries.append(RevisionItemSummary(
                item_id=item.id,
                label=item_label(rset.type, item.payload),
                reviews=reviews,
                success_rate=item_success,
                difficulty=difficulty,
                retrievability=retrievability(item.interval, last_reviewed, now),
                is_leech=is_leech,
                is_mature=is_mature,
                due=is_due,
            ))

        mastery_rate = round(mastered_count / items_count * 100, 1) if items_count else 0.0
        avg_success_rate = round(sum(success_rates) / len(success_rates), 1) if success_rates else 0.0
        true_retention = round(mature_successes / mature_reviews * 100, 1) if mature_reviews else 0.0
        avg_difficulty = round(sum(difficulties) / len(difficulties), 1) if difficulties else 0.0

        verdicts = self._build_verdicts(
            items_count, reviewed_items, leeches_count, due_count,
            true_retention, mature_reviews,
        )

        return RevisionSetStats(
            set_id=rset.id,
            type=rset.type,
            name=rset.name,
            items_count=items_count,
            reviewed_items=reviewed_items,
            mastered_count=mastered_count,
            mastery_rate=mastery_rate,
            avg_success_rate=avg_success_rate,
            true_retention=true_retention,
            leeches_count=leeches_count,
            due_count=due_count,
            avg_difficulty=avg_difficulty,
            verdicts=verdicts,
            items=item_summaries,
        )

    def _build_verdicts(self, items_count, reviewed_items, leeches, due, true_retention, mature_reviews) -> List[str]:
        verdicts = []
        if items_count == 0:
            return ["Ajoutez des éléments pour commencer à réviser."]
        if leeches:
            verdicts.append(f"{leeches} élément(s) « sangsue » à reformuler ou scinder.")
        if mature_reviews and true_retention < TARGET_RETENTION:
            verdicts.append(f"Rétention réelle {true_retention} % < cible {int(TARGET_RETENTION)} % : espacement peut-être trop agressif.")
        if due:
            verdicts.append(f"{due} élément(s) à réviser aujourd'hui.")
        if reviewed_items == 0:
            verdicts.append("Jamais révisé : lancez une première session.")
        if not verdicts:
            verdicts.append("Bonne progression — rien à signaler.")
        return verdicts
