from fastapi import APIRouter, Depends
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", summary="사용자 프로필 조회")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 프로필 정보를 반환합니다."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "email_opt_in": current_user.email_opt_in,
        "provider": current_user.provider
    }