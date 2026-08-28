from math import radians,sin,cos,asin,sqrt
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models import TechnicianProfile, User
from app.services.ads import public_ads
from app.schemas import AdOut, TechnicianOut

router=APIRouter(prefix="/public", tags=["public"])

def distance(a,b,c,d):
    p=radians(1); a,b,c,d=a*p,b*p,c*p,d*p; x=sin((c-a)/2)**2+cos(a)*cos(c)*sin((d-b)/2)**2; return 6371*2*asin(sqrt(x))

@router.get("/ads",response_model=list[AdOut])
async def ads(category:str|None=None,city:str|None=None,db:AsyncSession=Depends(get_db)): return await public_ads(db,category,city)

@router.get("/technicians",response_model=list[TechnicianOut])
async def technicians(category:str|None=None,city:str|None=None,lat:float|None=None,lon:float|None=None,db:AsyncSession=Depends(get_db)):
    q=select(User,TechnicianProfile).join(TechnicianProfile).where(User.role=="technician",User.is_active.is_(True),TechnicianProfile.verified.is_(True))
    if category:q=q.where(TechnicianProfile.category==category)
    if city:q=q.where(TechnicianProfile.city==city)
    rows=(await db.execute(q)).all(); out=[]
    for u,p in rows:
        item=TechnicianOut(id=u.id,full_name=u.full_name,business_name=p.business_name,category=p.category,city=p.city,address=p.address,latitude=float(p.latitude) if p.latitude is not None else None,longitude=float(p.longitude) if p.longitude is not None else None,rating=float(p.rating),verified=p.verified)
        out.append((distance(lat,lon,float(p.latitude),float(p.longitude)) if lat is not None and lon is not None and p.latitude is not None and p.longitude is not None else 999999,item))
    out.sort(key=lambda x:x[0]); return [x[1] for x in out]
