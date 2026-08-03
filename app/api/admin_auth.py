from fastapi import APIRouter, HTTPException, status

from ..schemas.auth import LoginRequest, LoginResponse
from ..services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def admin_login(login_data: LoginRequest):
    auth_service = AuthService()
    if not auth_service.authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )

    access_token = auth_service.create_access_token(data={"sub": login_data.username})
    return LoginResponse(access_token=access_token)
