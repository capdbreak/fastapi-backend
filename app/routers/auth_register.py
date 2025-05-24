from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from jose import jwt, JWTError
import os

from app.database import get_db
from app.models import User, StockIndex, StockBATMMAAN

router = APIRouter()


class RegisterRequest(BaseModel):
    token: str
    selectedIndices: List[str]
    selectedStocks: List[str]


@router.post("/auth/register-complete")
def register_complete(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        payload_data = jwt.decode(
            payload.token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    user_id = payload_data["id"]
    email = payload_data["sub"]
    name = payload_data["name"]
    provider = payload_data["provider"]

    if db.query(User).filter_by(id=user_id).first():
        raise HTTPException(status_code=400, detail="이미 가입된 사용자입니다")

    user = User(
        id=user_id, email=email, name=name, provider=provider, email_opt_in=False
    )
    db.add(user)

    for ticker in payload.selectedIndices:
        index = db.query(StockIndex).filter_by(Ticker=ticker).first()
        if not index:
            raise HTTPException(
                status_code=400, detail=f"지수 {ticker}가 존재하지 않습니다"
            )
        user.interested_indices.append(index)

    for ticker in payload.selectedStocks:
        stock = db.query(StockBATMMAAN).filter_by(Ticker=ticker).first()
        if not stock:
            raise HTTPException(
                status_code=400, detail=f"종목 {ticker}가 존재하지 않습니다"
            )
        user.interested_stocks.append(stock)

    db.commit()
    return {"msg": "회원가입이 완료되었습니다"}
