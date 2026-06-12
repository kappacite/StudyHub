from datetime import date

from app.schemas.stats_schema import HeatmapItem


def test_heatmap_item_coerces_postgres_date_object_to_iso_string():
    # Sous PostgreSQL, func.date() renvoie un datetime.date : sans coercion,
    # Pydantic rejetait l'objet (champ `date: str`) -> 400 en prod.
    item = HeatmapItem(date=date(2026, 6, 12), duration=120, count=3)
    assert item.date == "2026-06-12"
    assert isinstance(item.date, str)


def test_heatmap_item_passes_through_sqlite_string():
    # Sous SQLite, func.date() renvoie déjà une chaîne.
    item = HeatmapItem(date="2026-06-12", duration=10, count=1)
    assert item.date == "2026-06-12"
