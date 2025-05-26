from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/settings", tags=["email"])


@router.post("/newsletter", summary="뉴스 레터 구독 설정")
def set_email_update(user_token: str, email_opt_in: bool, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_token).first()
    if not user:
        return {"error": "사용자를 찾을 수 없습니다."}
    user.email_opt_in = email_opt_in
    db.commit()
    return {"message": "뉴스 레터 구독 설정이 업데이트되었습니다.", "email_opt_in": user.email_opt_in, "email": user.email} 

