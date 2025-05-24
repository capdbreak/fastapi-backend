from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StockIndex, StockBATMMAAN

router = APIRouter()

@router.get("/tickers")
def get_tickers(type: str = Query(..., pattern="^(index|stock)$"), db: Session = Depends(get_db)):
    if type == "index":
        return [{"ticker": i.Ticker, "name": i.Name} for i in db.query(StockIndex).all()]
    elif type == "stock":
        return [{"ticker": s.Ticker, "name": s.Name} for s in db.query(StockBATMMAAN).all()]
