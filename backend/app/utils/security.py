from app.models.binder import Binder
from app.models.group import GroupBinder, GroupMember
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

def check_binder_access(db_session, binder_id: int, user_id: int, write_required: bool = False) -> Binder:
    binder = db_session.get(Binder, binder_id)
    if not binder:
        raise ResourceNotFoundError("Classeur introuvable.")
        
    if binder.user_id == user_id:
        return binder
        
    # Walk up parent chain to see if any parent binder is shared in a group the user is in
    curr_id = binder_id
    binder_ids = []
    while curr_id:
        binder_ids.append(curr_id)
        b = db_session.get(Binder, curr_id)
        curr_id = b.parent_id if b else None
        
    # Check if shared in a group where the user is a member/follower
    membership = (
        db_session.query(GroupMember)
        .join(GroupBinder, GroupMember.group_id == GroupBinder.group_id)
        .filter(
            GroupBinder.binder_id.in_(binder_ids),
            GroupMember.user_id == user_id
        )
        .first()
    )
    
    if not membership:
        raise ForbiddenError("Accès interdit à ce classeur.")
        
    if write_required:
        if membership.role == "follower":
            raise ForbiddenError("Les abonnés (followers) ne peuvent pas modifier le contenu du cours.")
            
        if membership.role == "member":
            # Find the permission from GroupBinder
            group_binder = (
                db_session.query(GroupBinder)
                .filter(
                    GroupBinder.binder_id.in_(binder_ids),
                    GroupBinder.group_id == membership.group_id
                )
                .first()
            )
            if group_binder and group_binder.permission == "read":
                raise ForbiddenError("Vous n'avez pas la permission d'écriture sur ce classeur.")
                
    return binder
