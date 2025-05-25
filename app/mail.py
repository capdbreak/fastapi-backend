from typing import List
from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_utilities import repeat_every
from pydantic import BaseModel, EmailStr
from os import getenv
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

@repeat_every(hours=1, minutes=0, seconds=0, wait_first=True)
async def test():
    html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[getenv("TEST_EMAIL")],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)