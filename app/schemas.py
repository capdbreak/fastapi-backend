from pydantic import BaseModel
from datetime import date
from typing import Optional


class LLMAnalysis(BaseModel):
    subject: Optional[str]
    valence: Optional[str]
    arousal: Optional[str]
    importance: Optional[str]

    model_config = {"from_attributes": True}


class NewsResponse(BaseModel):
    id: str
    ticker: str
    date: date
    title: str
    article: str
    real_url: str
    summary: Optional[str]
    llm_analysis: Optional[LLMAnalysis]

    model_config = {"from_attributes": True}
