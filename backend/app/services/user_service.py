from app.dao.user_dao import UserDAO
from app.schemas.user_schema import UserUpdate, UserResponse
from app.middlewares.error_handler import ResourceNotFoundError, ConflictError

class UserService:
    def __init__(self, user_dao: UserDAO):
        self._user_dao = user_dao

    def get_profile(self, user_id: int) -> UserResponse:
        user = self._user_dao.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Utilisateur introuvable.")
        return UserResponse.model_validate(user)

    def update_profile(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = self._user_dao.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Utilisateur introuvable.")
            
        # Si on met à jour l'email, vérifier s'il est déjà pris par un autre
        if data.email and data.email != user.email:
            existing = self._user_dao.get_by_email(data.email)
            if existing:
                raise ConflictError("Cette adresse email est déjà utilisée.")
            user.email = data.email
            
        # Si on met à jour le username, vérifier s'il est déjà pris
        if data.username and data.username != user.username:
            existing = self._user_dao.get_by_username(data.username)
            if existing:
                raise ConflictError("Ce nom d'utilisateur est déjà pris.")
            user.username = data.username
            
        # Si on met à jour le mot de passe
        if data.password:
            user.set_password(data.password)
            
        updated = self._user_dao.update(user)
        return UserResponse.model_validate(updated)

    def delete_account(self, user_id: int) -> None:
        user = self._user_dao.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Utilisateur introuvable.")
        self._user_dao.delete(user)
