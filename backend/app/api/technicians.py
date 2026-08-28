from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.deps import current_user, technician
from app.models import TechnicianProfile, User
from app.schemas import ProfileIn

router=APIRouter(prefix="/technicians",tags=["technicians"])

@router.post("/profile")
async def profile(data:ProfileIn,user:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    p=await db.scalar(select(TechnicianProfile).where(TechnicianProfile.user_id==user.id))
    if not p:p=TechnicianProfile(user_id=user.id); db.add(p)
    for k,v in data.model_dump().items(): setattr(p,k,v)
    p.verified=False
    await db.commit(); return {"ok":True,"verified":False,"message":"Profile saved; admin verification is required."}

@router.get("/me")
async def me(user:User=Depends(technician)):
    return {"id":str(user.id),"full_name":user.full_name,"role":user.role.value,"access":"active"}
