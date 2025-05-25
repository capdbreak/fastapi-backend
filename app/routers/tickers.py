from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StockIndex, StockBATMMAAN
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/tickers")
def get_tickers(type: str = Query(..., pattern="^(index|stock)$"), db: Session = Depends(get_db)):
    """
    사용자의 관심 종목 목록을 제공하는 API
    - 'type=index' → stock_index 테이블에서 모든 인덱스 종목 조회
    - 'type=stock' → stock_batmmaan 테이블에서 모든 개별 종목 조회

    요청 예시:
        GET /tickers?type=index
        GET /tickers?type=stock

    응답 예시 (전체 컬럼 포함):
        [
            { "Ticker": "AAPL", "Name": "Apple", "query": "Apple stock market" },
            ...
        ]
    """
    if type == "index":
        results = db.query(StockIndex).all()
    elif type == "stock":
        results = db.query(StockBATMMAAN).all()
    else:
        return []

    return jsonable_encoder(results)