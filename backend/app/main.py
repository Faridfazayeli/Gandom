from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, public, technicians, subscriptions, ads, messages, payments, ai, admin, health

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield

app=FastAPI(title=settings.app_name,version="11.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE"],allow_headers=["*"])
for r in [auth.router,public.router,technicians.router,subscriptions.router,ads.router,messages.router,payments.router,ai.router,admin.router,health.router]: app.include_router(r,prefix="/api/v1")
