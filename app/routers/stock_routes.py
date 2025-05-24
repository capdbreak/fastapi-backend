from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StockIndex, StockBATMMAAN

router = APIRouter(prefix="/stock", tags=["Stock"])

@router.get("/index-names", summary="지수 이름 목록 조회")
def get_index_names(db: Session = Depends(get_db)):
    indices = db.query(StockIndex).all()
    return [{"ticker": index.Ticker, "name": index.Name} for index in indices]

@router.get("/batmmaan-names", summary="BATMMAAN 종목 이름 목록 조회")
def get_stock_names(db: Session = Depends(get_db)):
    stocks = db.query(StockBATMMAAN).all()
    return [{"ticker": stock.Ticker, "name": stock.Name} for stock in stocks]
