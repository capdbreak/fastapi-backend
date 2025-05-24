from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import os
from sqlalchemy.orm import Session
from jose import jwt
from app.database import get_db
from app.models import User

router = APIRouter()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    data = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data=data)
        token_json = token_resp.json()

        if "access_token" not in token_json:
            raise HTTPException(status_code=400, detail="Google access token 발급 실패")

        access_token = token_json["access_token"]

        user_resp = await client.get(
            GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_resp.json()

    if not user_info.get("verified_email", False):
        raise HTTPException(
            status_code=400, detail="Google 이메일 인증이 되지 않은 계정입니다."
        )

    user_id = user_info["id"]
    email = user_info["email"]
    name = user_info["name"]
    provider = "google"

    token = jwt.encode(
        {"sub": email, "name": name, "id": user_id, "provider": provider},
        os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM"),
    )

    user = db.query(User).filter_by(id=user_id).first()

    if user:
        redirect_url = f"{FRONTEND_URL}/main?token={token}"
    else:
        new_user = User(
            id=user_id, email=email, name=name, provider=provider, email_opt_in=False
        )
        db.add(new_user)
        db.commit()

        redirect_url = f"{FRONTEND_URL}/interest?token={token}"

    return RedirectResponse(url=redirect_url)
