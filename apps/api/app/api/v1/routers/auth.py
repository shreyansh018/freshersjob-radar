from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token, generate_csrf_token, hash_password
from app.db.session import get_db
from app.models import User
from app.schemas.user import LoginRequest, RegisterRequest, UserOut
from app.services.auth_service import authenticate, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)) -> UserOut:
    rate_limit(request, "register", limit=5, window_seconds=300)
    if not settings.registration_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration is disabled")
    existing = (await db.execute(select(User).where(User.email == payload.email.lower().strip()))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(email=payload.email.lower().strip(), password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    rate_limit(request, "login", limit=10, window_seconds=300)
    user = await authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(str(user.id), user.role)
    csrf_token = generate_csrf_token()
    response.set_cookie(
        "frj_token",
        token,
        httponly=True,
        # Local Docker runs over plain HTTP; production (Vercel) must be Secure.
        secure=settings.cookie_secure_enabled,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        secure=settings.cookie_secure_enabled,
        samesite="lax",
        path="/",
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "csrf_token": csrf_token,
        "user": UserOut.model_validate(user).model_dump(mode="json"),
    }


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("frj_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/password-reset/request")
async def password_reset_request(request: Request) -> dict:
    rate_limit(request, "password_reset", limit=5, window_seconds=300)
    # Token delivery is infrastructure-dependent. This endpoint is intentionally
    # side-effect free in the local-first profile to avoid leaking account data.
    return {"ok": True, "message": "If the email exists, a reset flow is available in the database-backed flow."}
