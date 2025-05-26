from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models import User

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰을 검증하고 사용자 정보를 반환"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        email: str = payload.get("sub")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 유효하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"id": user_id, "email": email, "payload": payload}
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    """현재 사용자 정보를 데이터베이스에서 가져옴"""
    user = db.query(User).filter(User.id == token_data["id"]).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user
