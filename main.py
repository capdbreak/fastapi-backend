from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_google import router as google_router
from app.routers.auth_register import router as register_router
from app.routers.stock_routes import router as stock_router
from app.routers.email_update import router as email_update_router
from app.routers.users import router as users_router
from app.routers import tickers
from app.routers.news import router as news_router
from app.mail import send_newsletter

import app.create_tables
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def run_newsletter():
        try:
            await send_newsletter()
        except Exception as e:
            logging.error(f"Newsletter error: {e}")

    asyncio.create_task(run_newsletter())  # doesn't block startup
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://34.22.108.245:3000",
        "https://capdbreak-finance-flow.uk",
        "https:/api.capdbreak-finance-flow.uk",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(google_router)
app.include_router(register_router)
app.include_router(stock_router)
app.include_router(tickers.router)
app.include_router(news_router)
app.include_router(email_update_router)
app.include_router(users_router)