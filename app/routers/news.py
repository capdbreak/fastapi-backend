from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas import NewsResponse
from app.models import NewsArticle, LLMNews
from app.database import get_db

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/dates/{ticker}", response_model=list[str])
def get_available_dates(ticker: str, db: Session = Depends(get_db)):
    result = (
        db.query(NewsArticle.date)
        .filter(NewsArticle.ticker == ticker)
        .distinct()
        .order_by(NewsArticle.date.desc())
        .all()
    )
    return [r.date.isoformat() for r in result]


@router.get("/{ticker}/{date}", response_model=list[NewsResponse])
def get_news_by_ticker_and_date(ticker: str, date: str, db: Session = Depends(get_db)):
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="날짜 형식은 YYYY-MM-DD 이어야 합니다."
        )

    articles = (
        db.query(NewsArticle)
        .filter(NewsArticle.ticker == ticker, NewsArticle.date == parsed_date)
        .order_by(NewsArticle.id.asc())
        .all()
    )

    responses = []
    for article in articles:
        llm = db.query(LLMNews).filter(LLMNews.id == article.id).first()

        response = NewsResponse(
            id=article.id,
            ticker=article.ticker,
            date=article.date,
            title=article.title,
            article=article.article,
            real_url=article.real_url,
            summary=article.summary,
            subject=llm.subject if llm else None,
            valence=llm.valence if llm else None,
            arousal=llm.arousal if llm else None,
            importance=llm.importance if llm else None,
        )
        responses.append(response)
    return responses


@router.get("/{ticker}", response_model=list[NewsResponse])
def get_news_by_ticker(ticker: str, db: Session = Depends(get_db)):
    articles = (
        db.query(NewsArticle)
        .filter(NewsArticle.ticker == ticker)
        .order_by(NewsArticle.date.desc(), NewsArticle.id.asc())
        .all()
    )

    responses = []
    for article in articles:
        llm = db.query(LLMNews).filter(LLMNews.id == article.id).first()

        response = NewsResponse(
            id=article.id,
            ticker=article.ticker,
            date=article.date,
            title=article.title,
            article=article.article,
            real_url=article.real_url,
            summary=article.summary,
            subject=llm.subject if llm else None,
            valence=llm.valence if llm else None,
            arousal=llm.arousal if llm else None,
            importance=llm.importance if llm else None,
        )
        responses.append(response)

    return responses
