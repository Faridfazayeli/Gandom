from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.deps import admin
from app.models import User, TechnicianProfile, Advertisement, AdStatus, SubscriptionPlan, AdPlan

router=APIRouter(prefix="/admin",tags=["admin"])

@router.post("/technicians/{user_id}/verify")
async def verify_technician(user_id,user:User=Depends(admin),db:AsyncSession=Depends(get_db)):
    p=await db.scalar(select(TechnicianProfile).where(TechnicianProfile.user_id==user_id))
    if not p: raise HTTPException(404,"Profile not found")
    p.verified=True; await db.commit(); return {"ok":True}

@router.post("/ads/{ad_id}/approve")
async def approve_ad(ad_id,user:User=Depends(admin),db:AsyncSession=Depends(get_db)):
    ad=await db.get(Advertisement,ad_id)
    if not ad or ad.status!=AdStatus.PENDING_REVIEW: raise HTTPException(404,"Ad not awaiting review")
    plan=await db.get(AdPlan,ad.plan_id)
    now=datetime.now(timezone.utc); ad.starts_at=now; ad.ends_at=now+timedelta(days=plan.duration_days); ad.status=AdStatus.ACTIVE
    await db.commit(); return {"ok":True,"starts_at":ad.starts_at,"ends_at":ad.ends_at}

@router.post("/ads/{ad_id}/reject")
async def reject_ad(ad_id,user:User=Depends(admin),db:AsyncSession=Depends(get_db)):
    ad=await db.get(Advertisement,ad_id)
    if not ad: raise HTTPException(404,"Ad not found")
    ad.status=AdStatus.REJECTED; await db.commit(); return {"ok":True}

@router.get("/ads/pending")
async def pending_ads(user:User=Depends(admin),db:AsyncSession=Depends(get_db)):
    return (await db.execute(select(Advertisement).where(Advertisement.status==AdStatus.PENDING_REVIEW))).scalars().all()
