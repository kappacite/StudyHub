from flask_jwt_extended import create_access_token, create_refresh_token
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import LoginRequest, LoginResponse, RefreshResponse
from app.middlewares.error_handler import ConflictError, UnauthorizedError, ResourceNotFoundError

class AuthService:
    def __init__(self, user_dao: UserDAO):
        self._user_dao = user_dao

    def register(self, data: UserCreate) -> UserResponse:
        # Vérifier si l'email existe déjà
        if self._user_dao.get_by_email(data.email):
            raise ConflictError("Cette adresse email est déjà utilisée.")
            
        # Vérifier si le nom d'utilisateur existe déjà
        if self._user_dao.get_by_username(data.username):
            raise ConflictError("Ce nom d'utilisateur est déjà pris.")
            
        # Création de l'utilisateur
        user = User(email=data.email, username=data.username)
        user.set_password(data.password)
        
        created = self._user_dao.create(user)
        return UserResponse.model_validate(created)

    def login(self, data: LoginRequest) -> LoginResponse:
        user = self._user_dao.get_by_email(data.email)
        if not user or not user.check_password(data.password):
            raise UnauthorizedError("Identifiants de connexion invalides.")
            
        if not user.is_active:
            raise UnauthorizedError("Ce compte a été désactivé.")
            
        # Génération des tokens JWT (identité = ID de l'utilisateur sous forme de chaîne)
        identity = str(user.id)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user)
        )

    def refresh_access_token(self, user_identity: str) -> RefreshResponse:
        # L'identité reçue est déjà validée par le décorateur jwt_required(refresh=True) de Flask-JWT-Extended
        access_token = create_access_token(identity=user_identity)
        return RefreshResponse(access_token=access_token)

    def delete_account(self, user_id: int) -> None:
        user = self._user_dao.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Utilisateur introuvable.")
        self._user_dao.delete(user)
