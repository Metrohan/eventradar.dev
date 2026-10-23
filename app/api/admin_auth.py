from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..schemas.auth import LoginRequest, LoginResponse
from ..services.auth_service import AuthService

from ..services.rate_limiter import FixedWindowRateLimiter, client_key

router = APIRouter()
login_limiter = FixedWindowRateLimiter(limit=10, window_seconds=60)


def enforce_login_rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    retry_after = login_limiter.check(client_key(key))
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(max(1, ceil(retry_after)))},
        )


@router.post("/login", response_model=LoginResponse)
async def admin_login(
    login_data: LoginRequest,
    _rate_limit: None = Depends(enforce_login_rate_limit),
):
    auth_service = AuthService()
    if not auth_service.authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )

    access_token = auth_service.create_access_token(data={"sub": login_data.username})
    return LoginResponse(access_token=access_token)
