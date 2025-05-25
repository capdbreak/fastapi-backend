from pydantic import BaseModel
from datetime import date
from typing import Optional


class LLMAnalysis(BaseModel):
    subject: Optional[str]
    valence: Optional[str]
    arousal: Optional[str]
    importance: Optional[str]


class NewsResponse(BaseModel):
    id: str
    ticker: str
    date: date
    title: str
    article: str
    real_url: str
    summary: str | None = None
    subject: str | None = None
    valence: str | None = None
    arousal: str | None = None
    importance: str | None = None
