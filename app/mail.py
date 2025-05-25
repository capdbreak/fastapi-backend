from typing import List
from fastapi import BackgroundTasks, FastAPI
from fastapi_utilities import repeat_at
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from os import getenv
import logging
from app.database import get_db
from app.llm import get_summaries_for_user
from app.models import User
class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = getenv("MAIL_PASSWORD"),
    MAIL_FROM = getenv("MAIL_FROM"),
    MAIL_PORT = getenv("MAIL_PORT"),
    MAIL_SERVER = getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
logger = logging.getLogger(__name__)

def build_email_body(user_name: str, summaries: list[dict]) -> str:
    lines = [f"안녕하세요 {user_name}님, 오늘의 요약 뉴스입니다.\n"]

    for item in summaries:
        lines.append(f"[{item['ticker']}] {item['title']}")
        lines.append(f"요약: {item['summary']}\n")

    lines.append("좋은 하루 보내세요!")
    return "\n".join(lines)


db = get_db()

@repeat_at(cron="0 0 * * *", raise_exceptions=True)
async def send_newsletter():
    """
    Sends a test email to the address specified in TEST_EMAIL env var.
    """
    user_list = db.query(User).filter(User.email_opt_in == True).all()

    for user in user_list:
        summaries = get_summaries_for_user(user, db)
        if summaries:
            body = build_email_body(user.name, summaries)
            html = f"<p>{body.replace('\n', '<br>')}</p>"
            fm = FastMail(conf)
            message = MessageSchema(
                subject="오늘의 요약 뉴스",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html,
            )
            await fm.send_message(message)
            logger.info(f"Newsletter sent to {user.email}")