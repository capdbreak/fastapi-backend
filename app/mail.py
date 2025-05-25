from typing import List
from fastapi_utilities import repeat_every
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from os import getenv
import logging


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=getenv("MAIL_PASSWORD"),
    MAIL_FROM=getenv("MAIL_FROM"),
    MAIL_PORT=getenv("MAIL_PORT"),
    MAIL_SERVER=getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)
logger = logging.getLogger(__name__)


@repeat_every(seconds=60 * 60 * 24, raise_exceptions=True)
async def send_test_email():
    """
    Sends a test email to the address specified in TEST_EMAIL env var.
    """
    html = """<p>Hi, this is a test mail. Thanks for using FastAPI-Mail!</p>"""
    message = MessageSchema(
        subject="FastAPI-Mail Test",
        recipients=[getenv("TEST_EMAIL")],  # Use TEST_EMAIL env var
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Test email sent to {getenv('TEST_EMAIL')}")
