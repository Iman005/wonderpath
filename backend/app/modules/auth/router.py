"""Auth HTTP routes."""
from fastapi import APIRouter, Depends

from app.infrastructure.db.models import User
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.dtos import AuthTokenOut, GoogleLoginIn, PasswordLoginIn, RegisterIn, UserOut, to_user_out
from app.modules.auth.service import AuthService
from app.modules.identity.auth_dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/google", response_model=AuthTokenOut)
def login_with_google(payload: GoogleLoginIn, service: AuthService = Depends(get_auth_service)) -> AuthTokenOut:
    return service.login_with_google(id_token=payload.id_token, access_token=payload.access_token)


@router.post("/register", response_model=AuthTokenOut)
def register(payload: RegisterIn, service: AuthService = Depends(get_auth_service)) -> AuthTokenOut:
    return service.register(payload.email, payload.password, payload.display_name)


@router.post("/login", response_model=AuthTokenOut)
def login_with_password(payload: PasswordLoginIn, service: AuthService = Depends(get_auth_service)) -> AuthTokenOut:
    return service.login_with_password(payload.email, payload.password)


@router.post("/dev", response_model=AuthTokenOut)
def login_dev(service: AuthService = Depends(get_auth_service)) -> AuthTokenOut:
    """Local development login — only works when ENV=development and ALLOW_DEV_LOGIN."""
    return service.login_dev()


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return to_user_out(user)
