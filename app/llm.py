import os
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import LLMNews, User, user_index_interest, user_stock_interest, NewsArticle

LLM_BACKEND_URL = os.getenv("LLM_SERVER_URL")
ARTICLES_PER_TICKER = 10  # Number of articles to fetch per ticker
SUMMARY_MIN_LEN = 150
SUMMARY_MAX_LEN = 400
SUMMARY_MAX_COUNT = 5

logger = logging.getLogger(__name__)


async def get_summaries_for_user(user: User, db: Session) -> List[Dict]:
    """
    Fetches news articles for the user's interested tickers, sends them to the LLM backend,
    and returns the best summaries.
    """
    summaries = []

    index_interests = db.query(user_index_interest).filter_by(user_id=user.id).all()
    stock_interests = db.query(user_stock_interest).filter_by(user_id=user.id).all()
    tickers = list({row.ticker for row in index_interests + stock_interests})

    logger.info(f"Interested tickers for user {user.id}: {tickers}")

    for ticker in tickers:
        # Query both NewsArticle and LLMNews
        results = (
            db.query(NewsArticle, LLMNews)
            .join(LLMNews, NewsArticle.id == LLMNews.id)
            .filter(NewsArticle.ticker == ticker)
            .order_by(NewsArticle.id.desc())
            .limit(ARTICLES_PER_TICKER)
            .all()
        )
        logger.info(f"Retrieved {len(results)} news articles for ticker {ticker}")

        if not results:
            continue

        for article, llm_news in results:
            summaries.append(
                {
                    "ticker": ticker,
                    "title": article.title,
                    "summary": llm_news.summary,
                    "importance": llm_news.importance,
                    "arousal": llm_news.arousal,
                    "valence": llm_news.valence,
                    "real_url": article.real_url
                }
            )

    return select_best_summaries(
        summaries,
        min_len=SUMMARY_MIN_LEN,
        max_len=SUMMARY_MAX_LEN,
        max_count=SUMMARY_MAX_COUNT,
    )


def select_best_summaries(
    summaries: List[Dict], min_len: int = 150, max_len: int = 400, max_count: int = 5
) -> List[Dict]:
    """
    Selects the best summaries based on length and importance/arousal/valence.
    """

    def summary_len(s: Dict) -> int:
        return len(s.get("summary", ""))
    
    def safe_float(value, default=0.0):
        """Convert string values to float safely"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    # Filter summaries within length range
    in_range = [s for s in summaries if min_len <= summary_len(s) <= max_len]

    # If none in range, take the shortest longer summaries
    if not in_range:
        over_range = [s for s in summaries if summary_len(s) > max_len]
        over_range.sort(key=summary_len)
        in_range = over_range

    # Sort by importance, then arousal, then valence (all descending)
    in_range.sort(
        key=lambda s: (
            -safe_float(s.get("importance")),
            -safe_float(s.get("arousal")),
            -safe_float(s.get("valence")),
        )
    )

    return in_range[:max_count]
