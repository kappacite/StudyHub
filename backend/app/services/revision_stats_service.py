import math
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass, field
from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
from app.dao.study_session_dao import StudySessionDAO
from app.dao.binder_dao import BinderDAO
from app.models.revision import RevisionSet, RevisionItem
from app.models.study_session import StudySession
from app.schemas.revision_schema import (
    RevisionItemStats, RevisionSetStats, RevisionHistoryPoint, RevisionItemSummary,
    RevisionSetSummary, RevisionTypeBreakdown, RevisionBinderStats,
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


@dataclass
class _SetAggregate:
    """Métriques d'un ensemble + accumulateurs bruts (recomposables au niveau classeur)."""
    set: RevisionSet
    items_count: int = 0
    reviewed_items: int = 0
    mastered_count: int = 0
    leeches_count: int = 0
    due_count: int = 0
    mature_reviews: int = 0
    mature_successes: int = 0
    success_rates: list = field(default_factory=list)   # par item révisé
    difficulties: list = field(default_factory=list)     # par item
    item_summaries: list = field(default_factory=list)

    @property
    def mastery_rate(self) -> float:
        return round(self.mastered_count / self.items_count * 100, 1) if self.items_count else 0.0

    @property
    def avg_success_rate(self) -> float:
        return round(sum(self.success_rates) / len(self.success_rates), 1) if self.success_rates else 0.0

    @property
    def true_retention(self) -> float:
        return round(self.mature_successes / self.mature_reviews * 100, 1) if self.mature_reviews else 0.0

    @property
    def avg_difficulty(self) -> float:
        return round(sum(self.difficulties) / len(self.difficulties), 1) if self.difficulties else 0.0


class RevisionStatsService:
    def __init__(self, set_dao: RevisionSetDAO, item_dao: RevisionItemDAO,
                 session_dao: StudySessionDAO, binder_dao: BinderDAO = None):
        self._set_dao = set_dao
        self._item_dao = item_dao
        self._session_dao = session_dao
        self._binder_dao = binder_dao or BinderDAO(set_dao.db)

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

    def _aggregate_set(self, rset: RevisionSet, items: List[RevisionItem],
                       by_item: dict, now: datetime) -> _SetAggregate:
        """Calcule les métriques d'un ensemble à partir d'items + sessions déjà chargés
        (aucune requête ici : appelable en boucle sans N+1)."""
        agg = _SetAggregate(set=rset, items_count=len(items))
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
                agg.reviewed_items += 1
                agg.success_rates.append(item_success)
            agg.difficulties.append(difficulty)
            if is_mature:
                agg.mastered_count += 1
                agg.mature_reviews += reviews
                agg.mature_successes += successes
            if is_leech:
                agg.leeches_count += 1
            if is_due:
                agg.due_count += 1

            agg.item_summaries.append(RevisionItemSummary(
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
        return agg

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

        agg = self._aggregate_set(rset, items, by_item, now)
        verdicts = self._build_verdicts(
            agg.items_count, agg.reviewed_items, agg.leeches_count, agg.due_count,
            agg.true_retention, agg.mature_reviews,
        )

        return RevisionSetStats(
            set_id=rset.id,
            type=rset.type,
            name=rset.name,
            items_count=agg.items_count,
            reviewed_items=agg.reviewed_items,
            mastered_count=agg.mastered_count,
            mastery_rate=agg.mastery_rate,
            avg_success_rate=agg.avg_success_rate,
            true_retention=agg.true_retention,
            leeches_count=agg.leeches_count,
            due_count=agg.due_count,
            avg_difficulty=agg.avg_difficulty,
            verdicts=verdicts,
            items=agg.item_summaries,
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

    # --- Classeur (A8) --------------------------------------------------------

    def get_binder_stats(self, user_id: int, binder_id, include_descendants: bool = True) -> RevisionBinderStats:
        """Agrège les stats de tous les ensembles de révision d'un classeur (et,
        par défaut, de son sous-arbre). Les decks de flashcards ont leurs stats
        propres (`/stats/decks/:id`) et ne sont pas inclus ici."""
        from app.utils.security import check_binder_access

        # Vérifie l'accès (propriétaire OU classe partagée) ; lève 404/403.
        binder = check_binder_access(self._set_dao.db, binder_id, user_id, write_required=False)

        binder_internal_ids = [binder._id]
        if include_descendants:
            binder_internal_ids += [b._id for b in self._binder_dao.get_descendants(binder._id)]

        now = datetime.utcnow()
        sets = self._set_dao.get_by_binders(binder_internal_ids)
        set_ids = [s.id for s in sets]

        # Items de tous les ensembles en une requête, regroupés par ensemble.
        items = self._item_dao.get_by_sets(set_ids)
        items_by_set: dict = {}
        for it in items:
            items_by_set.setdefault(it.set_id, []).append(it)

        # Sessions : une requête par type d'ensemble présent (≤ 5), pas par item.
        ids_by_type: dict = {}
        for s in sets:
            for it in items_by_set.get(s.id, []):
                ids_by_type.setdefault(s.type, []).append(it.id)
        by_item: dict = {}
        for set_type, ids in ids_by_type.items():
            for sess in self._session_dao.get_for_items(ids, set_type):
                by_item.setdefault(sess.item_id, []).append(sess)

        # Agrégation par ensemble (réutilise la logique de get_set_stats).
        summaries: List[RevisionSetSummary] = []
        by_type_acc: dict = {}   # type -> [sets, items, mastered]
        tot = _SetAggregate(set=binder)   # accumulateur global

        for rset in sets:
            agg = self._aggregate_set(rset, items_by_set.get(rset.id, []), by_item, now)
            summaries.append(RevisionSetSummary(
                set_id=rset.id, type=rset.type, name=rset.name,
                items_count=agg.items_count, reviewed_items=agg.reviewed_items,
                mastered_count=agg.mastered_count, mastery_rate=agg.mastery_rate,
                avg_success_rate=agg.avg_success_rate, true_retention=agg.true_retention,
                leeches_count=agg.leeches_count, due_count=agg.due_count,
                avg_difficulty=agg.avg_difficulty,
            ))
            tot.items_count += agg.items_count
            tot.reviewed_items += agg.reviewed_items
            tot.mastered_count += agg.mastered_count
            tot.leeches_count += agg.leeches_count
            tot.due_count += agg.due_count
            tot.mature_reviews += agg.mature_reviews
            tot.mature_successes += agg.mature_successes
            tot.success_rates.extend(agg.success_rates)
            tot.difficulties.extend(agg.difficulties)

            acc = by_type_acc.setdefault(rset.type, [0, 0, 0])
            acc[0] += 1
            acc[1] += agg.items_count
            acc[2] += agg.mastered_count

        by_type = [
            RevisionTypeBreakdown(
                type=t, sets_count=a[0], items_count=a[1], mastered_count=a[2],
                mastery_rate=round(a[2] / a[1] * 100, 1) if a[1] else 0.0,
            )
            for t, a in sorted(by_type_acc.items())
        ]

        # Ensembles les plus à risque : sangsues d'abord, puis faible maîtrise.
        weakest = sorted(
            [s for s in summaries if s.items_count > 0],
            key=lambda s: (-s.leeches_count, s.mastery_rate, -s.due_count),
        )[:5]

        verdicts = self._build_verdicts(
            tot.items_count, tot.reviewed_items, tot.leeches_count, tot.due_count,
            tot.true_retention, tot.mature_reviews,
        )

        return RevisionBinderStats(
            binder_id=binder.id,
            name=binder.name,
            include_descendants=include_descendants,
            sets_count=len(sets),
            items_count=tot.items_count,
            reviewed_items=tot.reviewed_items,
            mastered_count=tot.mastered_count,
            mastery_rate=tot.mastery_rate,
            avg_success_rate=tot.avg_success_rate,
            true_retention=tot.true_retention,
            leeches_count=tot.leeches_count,
            due_count=tot.due_count,
            avg_difficulty=tot.avg_difficulty,
            by_type=by_type,
            sets=summaries,
            weakest_sets=weakest,
            verdicts=verdicts,
        )
