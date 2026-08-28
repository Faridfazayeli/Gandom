from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_token
from app.models import User, Role
from app.schemas import RegisterIn, LoginIn, TokenOut

router=APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
async def register(data:RegisterIn, db:AsyncSession=Depends(get_db)):
    role=data.role if data.role in {r.value for r in Role if r!=Role.ADMIN} else Role.GENERAL
    if await db.scalar(select(User).where(User.phone==data.phone)): raise HTTPException(409,"Phone already registered")
    user=User(phone=data.phone,password_hash=hash_password(data.password),full_name=data.full_name,role=role,phone_verified=False)
    db.add(user); await db.commit(); await db.refresh(user)
    return TokenOut(access_token=create_token(user.id,user.role.value,"access",timedelta(minutes=settings.access_token_minutes)), refresh_token=create_token(user.id,user.role.value,"refresh",timedelta(days=settings.refresh_token_days)))

@router.post("/login", response_model=TokenOut)
async def login(data:LoginIn, db:AsyncSession=Depends(get_db)):
    user=await db.scalar(select(User).where(User.phone==data.phone))
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid credentials")
    return TokenOut(access_token=create_token(user.id,user.role.value,"access",timedelta(minutes=settings.access_token_minutes)), refresh_token=create_token(user.id,user.role.value,"refresh",timedelta(days=settings.refresh_token_days)))

@router.post("/verify-phone")
async def verify_phone(phone:str, code:str, db:AsyncSession=Depends(get_db)):
    user=await db.scalar(select(User).where(User.phone==phone))
    if not user: raise HTTPException(404,"User not found")
    if code != "000000": raise HTTPException(400,"Invalid verification code")
    user.phone_verified=True; await db.commit(); return {"verified":True}
