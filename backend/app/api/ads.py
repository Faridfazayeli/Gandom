from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.deps import technician
from app.models import AdPlan, Advertisement, AdStatus, User
from app.schemas import AdCreate, AdOut, PlanOut
from app.services.payments import PaymentService

router=APIRouter(prefix="/ads",tags=["ads"])

@router.get("/plans",response_model=list[PlanOut])
async def plans(db:AsyncSession=Depends(get_db)): return (await db.execute(select(AdPlan).where(AdPlan.active.is_(True)).order_by(AdPlan.duration_days))).scalars().all()

@router.post("",response_model=AdOut)
async def create(data:AdCreate,user:User=Depends(technician),db:AsyncSession=Depends(get_db)):
    plan=await db.get(AdPlan,data.plan_id)
    if not plan or not plan.active: raise HTTPException(404,"Ad plan not found")
    ad=Advertisement(owner_id=user.id,title=data.title,description=data.description,category=data.category,city=data.city,latitude=data.latitude,longitude=data.longitude,status=AdStatus.PENDING_PAYMENT,plan_id=plan.id)
    db.add(ad); await db.commit(); await db.refresh(ad)
    p=await PaymentService().create(db,user.id,"ad",plan.price,plan.currency,{"ad_id":str(ad.id),"plan_id":str(plan.id)})
    return ad

@router.get("/mine",response_model=list[AdOut])
async def mine(user:User=Depends(technician),db:AsyncSession=Depends(get_db)): return (await db.execute(select(Advertisement).where(Advertisement.owner_id==user.id).order_by(Advertisement.created_at.desc()))).scalars().all()
