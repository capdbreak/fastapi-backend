from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
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


@router.get("/profile/{user_id}", summary="특정 사용자 프로필 조회")
async def get_specific_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 사용자의 프로필을 조회합니다. (관리자용 또는 자신의 정보만)"""
    # 자신의 정보만 조회할 수 있도록 제한
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="자신의 프로필만 조회할 수 있습니다."
        )
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "email_opt_in": current_user.email_opt_in,
        "provider": current_user.provider
    }
