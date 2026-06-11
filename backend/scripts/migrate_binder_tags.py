from app import create_app
from app.extensions import db
from app.models.tag import Tag
from sqlalchemy import inspect, text


def migrate_binder_tags() -> None:
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        binder_columns = {column["name"] for column in inspector.get_columns("binders")}
        if "tags" not in binder_columns:
            return

        rows = db.session.execute(text("SELECT id, user_id, tags FROM binders WHERE tags IS NOT NULL")).mappings()
        for row in rows:
            legacy_tags = row["tags"]
            if isinstance(legacy_tags, str):
                import json
                legacy_tags = json.loads(legacy_tags)
            if not isinstance(legacy_tags, list):
                continue
            for raw_name in legacy_tags:
                name = " ".join(str(raw_name).strip().split())
                if not name:
                    continue
                tag = db.session.query(Tag).filter_by(user_id=row["user_id"], name=name).first()
                if not tag:
                    tag = Tag(user_id=row["user_id"], name=name)
                    db.session.add(tag)
                    db.session.flush()
                existing_link = db.session.execute(
                    text("SELECT 1 FROM binder_tags WHERE binder_id = :binder_id AND tag_id = :tag_id"),
                    {"binder_id": row["id"], "tag_id": tag.id},
                ).first()
                if not existing_link:
                    db.session.execute(
                        text("INSERT INTO binder_tags (binder_id, tag_id) VALUES (:binder_id, :tag_id)"),
                        {"binder_id": row["id"], "tag_id": tag.id},
                    )
        db.session.commit()


if __name__ == "__main__":
    migrate_binder_tags()
