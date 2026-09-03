"""Tests directs de app.dao.revision_dao (requete SQL, pas la couche HTTP) --
notes-ia-planning-corrections, Task 1 : nouvelle methode get_items_due_between
utilisee par le planning pour agreger les RevisionItem (jusque-la jamais pris
en compte, cf. CONTEXT.md du chantier)."""

from datetime import datetime, timedelta

from app.extensions import db
from app.dao.revision_dao import RevisionItemDAO
from app.models.revision import RevisionSet, RevisionItem


def test_get_items_due_between_scoped_to_user_and_range(app, test_user):
    with app.app_context():
        dao = RevisionItemDAO(db.session)
        rset = RevisionSet(name="Ensemble", user_id=test_user["id"])
        db.session.add(rset)
        db.session.commit()

        due_now = RevisionItem(
            set_id=rset.id, type="vf", payload={"assertion": "A", "correct": True},
            next_review=datetime.utcnow(),
        )
        due_next_week = RevisionItem(
            set_id=rset.id, type="vf", payload={"assertion": "B", "correct": True},
            next_review=datetime.utcnow() + timedelta(days=7),
        )
        db.session.add_all([due_now, due_next_week])
        db.session.commit()

        result = dao.get_items_due_between(
            test_user["id"], datetime.min, datetime.utcnow() + timedelta(hours=1)
        )

        assert [i.id for i in result] == [due_now.id]
        # revision_set deja charge (joinedload), pas de requete supplementaire attendue.
        assert result[0].revision_set.name == "Ensemble"
