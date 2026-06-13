import math
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy import or_, func
from app.extensions import db
from app.models.binder import Binder
from app.models.note import Note
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.diagram import Diagram
from app.models.pdf_document import PDFDocument
from app.models.tag import Tag
from app.schemas.binder_schema import BinderResponse
from app.middlewares.error_handler import ResourceNotFoundError

class CommunityService:
    def list_public_packages(
        self, 
        search: Optional[str] = None, 
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[BinderResponse], int]:
        query = db.session.query(Binder).filter(Binder.is_public == True)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Binder.name.ilike(search_pattern),
                    Binder.description.ilike(search_pattern),
                    Binder.tags.any(Tag.name.ilike(search_pattern))
                )
            )
            
        # Tri par fork_count desc et date de création desc
        query = query.order_by(Binder.fork_count.desc(), Binder.created_at.desc())

        total = query.count()
        offset = (page - 1) * per_page
        # Préchargement des tags : BinderResponse.tags sinon chargé en lazy par package (N+1).
        from sqlalchemy.orm import selectinload
        binders = query.options(selectinload(Binder.tags)).limit(per_page).offset(offset).all()
        
        return [BinderResponse.model_validate(b) for b in binders], total

    def clone_package(self, user_id: int, binder_id) -> BinderResponse:
        # 1. Récupérer le classeur source
        # Il doit être public, appartenir à l'utilisateur, ou être partagé dans un de ses groupes/classes
        parent_binder = db.session.query(Binder).filter(Binder.id == str(binder_id)).first()
        if not parent_binder:
            raise ResourceNotFoundError("Package/Classeur introuvable.")
            
        if parent_binder.user_id != user_id and not parent_binder.is_public:
            from app.models.group import GroupBinder, GroupMember
            curr_binder = parent_binder
            binder_ids = []
            while curr_binder:
                binder_ids.append(curr_binder._id)
                curr_binder = curr_binder.parent
                
            membership = (
                db.session.query(GroupMember)
                .join(GroupBinder, GroupMember.group_id == GroupBinder.group_id)
                .filter(
                    GroupBinder.binder_id.in_(binder_ids),
                    GroupMember.user_id == user_id
                )
                .first()
            )
            if not membership:
                raise ResourceNotFoundError("Package/Classeur public introuvable.")

              # 2. Fonction récursive de clonage profond
        def clone_binder_recursive(old_binder: Binder, new_parent_id: Optional[int] = None) -> Binder:
            new_binder = Binder(
                name=old_binder.name,
                user_id=user_id,
                parent_id=new_parent_id,
                is_public=False,  # Un package cloné est privé par défaut dans l'espace de l'utilisateur
                description=old_binder.description,
                original_author_id=old_binder.original_author_id or old_binder.user_id,
                fork_count=0
            )
            new_binder.tags = [
                get_or_create_user_tag(old_tag.name, old_tag.color)
                for old_tag in old_binder.tags
            ]
            db.session.add(new_binder)
            db.session.flush()  # Pour obtenir le nouvel ID
            
            # --- Cloner les Notes et leurs Decks Fantômes associés ---
            for old_note in old_binder.notes:
                new_note = Note(
                    title=old_note.title,
                    content=old_note.content,
                    user_id=user_id,
                    binder_id=new_binder._id
                )
                db.session.add(new_note)
                db.session.flush()
                
                # Vérifier s'il y a un deck fantôme associé à l'ancienne note
                old_deck = db.session.query(Deck).filter_by(note_id=old_note._id).first()
                if old_deck:
                    new_deck = Deck(
                        name=old_deck.name,
                        description=old_deck.description,
                        user_id=user_id,
                        binder_id=new_binder._id,
                        note_id=new_note._id
                    )
                    db.session.add(new_deck)
                    db.session.flush()
                    
                    # Cloner les cartes et réinitialiser l'état SM-2
                    for old_card in old_deck.cards:
                        new_card = Flashcard(
                            deck_id=new_deck.id,
                            front=old_card.front,
                            back=old_card.back,
                            placeholder_hash=old_card.placeholder_hash,
                            original_text=old_card.original_text,
                            ease_factor=2.5,
                            interval=0,
                            repetitions=0,
                            next_review=func.now()
                        )
                        db.session.add(new_card)
 
            # --- Cloner les Decks classiques (non liés à des notes) ---
            for old_deck in old_binder.decks:
                if old_deck.note_id is None:
                    new_deck = Deck(
                        name=old_deck.name,
                        description=old_deck.description,
                        user_id=user_id,
                        binder_id=new_binder._id
                    )
                    db.session.add(new_deck)
                    db.session.flush()
                    
                    for old_card in old_deck.cards:
                        new_card = Flashcard(
                            deck_id=new_deck.id,
                            front=old_card.front,
                            back=old_card.back,
                            placeholder_hash=old_card.placeholder_hash,
                            original_text=old_card.original_text,
                            ease_factor=2.5,
                            interval=0,
                            repetitions=0,
                            next_review=func.now()
                        )
                        db.session.add(new_card)
 
            # --- Cloner les Diagrammes ---
            for old_diag in old_binder.diagrams:
                new_diag = Diagram(
                    title=old_diag.title,
                    code=old_diag.code,
                    user_id=user_id,
                    binder_id=new_binder._id
                )
                db.session.add(new_diag)
 
            # --- Cloner les Documents PDF ---
            for old_pdf in old_binder.pdfs:
                new_pdf = PDFDocument(
                    filename=old_pdf.filename,
                    name=old_pdf.name,
                    user_id=user_id,
                    binder_id=new_binder._id
                )
                db.session.add(new_pdf)
 
            # --- Cloner les classeurs enfants ---
            for child in old_binder.children:
                clone_binder_recursive(child, new_binder._id)

            return new_binder

        def get_or_create_user_tag(name: str, color: str | None):
            tag = db.session.query(Tag).filter_by(user_id=user_id, name=name).first()
            if tag:
                return tag
            tag = Tag(user_id=user_id, name=name, color=color)
            db.session.add(tag)
            db.session.flush()
            return tag

        # 3. Exécuter le clonage à partir du classeur racine
        cloned_binder = clone_binder_recursive(parent_binder, parent_binder.parent_id)
        
        # 4. Incrémenter le fork_count sur l'original si ce n'est pas le nôtre
        if parent_binder.user_id != user_id:
            parent_binder.fork_count += 1
            
        db.session.commit()
        
        return BinderResponse.model_validate(cloned_binder)
