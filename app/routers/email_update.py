from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


class NewsletterSettingsRequest(BaseModel):
    email_opt_in: bool = Field(..., description="뉴스레터 구독 여부")

@router.post("/newsletter", summary="뉴스 레터 구독 설정")
async def set_email_update(
    request: NewsletterSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """뉴스레터 구독 설정을 업데이트합니다."""
    current_user.email_opt_in = request.email_opt_in
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "뉴스 레터 구독 설정이 업데이트되었습니다.", 
        "email_opt_in": current_user.email_opt_in, 
        "email": current_user.email
    }


@router.get("/newsletter", summary="뉴스 레터 구독 설정 조회")
async def get_email_settings(current_user: User = Depends(get_current_user)):
    """현재 뉴스레터 구독 설정을 조회합니다."""
    return {
        "email_opt_in": current_user.email_opt_in,
        "email": current_user.email
    }
