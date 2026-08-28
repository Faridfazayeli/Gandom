from math import radians, sin, cos, asin, sqrt
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models import TechnicianProfile, User, Advertisement, AdStatus
from app.services.ads import public_ads
from app.services.search import SearchService
from app.schemas import AdOut, TechnicianOut

router = APIRouter(prefix="/public", tags=["public"])
search_service = SearchService()

def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km using Haversine formula."""
    p = radians(1)
    lat1, lon1, lat2, lon2 = lat1*p, lon1*p, lat2*p, lon2*p
    x = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 6371 * 2 * asin(sqrt(x))


@router.get("/ads", response_model=list[AdOut], summary="دریافت آگهی‌های عمومی")
async def ads(
    category: Optional[str] = Query(None, description="دسته‌بندی"),
    city: Optional[str] = Query(None, description="شهر"),
    search: Optional[str] = Query(None, description="جستجو در عنوان و توضیحات"),
    db: AsyncSession = Depends(get_db)
):
    """
    دریافت آگهی‌های فعال عمومی
    - **category**: فیلتر بر اساس دسته‌بندی
    - **city**: فیلتر بر اساس شهر
    - **search**: جستجو متنی
    """
    if search:
        return await search_service.search_ads(
            db, 
            query=search, 
            category=category, 
            city=city
        )
    return await public_ads(db, category, city)


@router.get("/technicians", response_model=list[TechnicianOut], summary="دریافت فهرست تکنسین‌ها")
async def technicians(
    category: Optional[str] = Query(None, description="دسته‌بندی تخصص"),
    city: Optional[str] = Query(None, description="شهر"),
    lat: Optional[float] = Query(None, description="عرض جغرافیایی"),
    lon: Optional[float] = Query(None, description="طول جغرافیایی"),
    search: Optional[str] = Query(None, description="جستجو در نام یا کسب‌وکار"),
    radius: Optional[float] = Query(10, description="شعاع جستجوی مکانی (کیلومتر)"),
    db: AsyncSession = Depends(get_db)
):
    """
    دریافت فهرست تکنسین‌های تایید‌شده
    
    ### پارامترها:
    - **category**: فیلتر بر اساس دسته‌بندی
    - **city**: فیلتر بر اساس شهر
    - **lat/lon**: مختصات برای جستجوی مکانی
    - **search**: جستجوی متنی در نام و کسب‌وکار
    - **radius**: شعاع جستجوی مکانی
    """
    
    # اگر مختصات موجود است، جستجوی مکانی را انجام بده
    if lat is not None and lon is not None:
        results = await search_service.search_by_location(
            db, 
            latitude=lat, 
            longitude=lon, 
            radius_km=radius, 
            category=category
        )
        return [
            TechnicianOut(
                id=user.id,
                full_name=user.full_name,
                business_name=profile.business_name,
                category=profile.category,
                city=profile.city,
                address=profile.address,
                latitude=float(profile.latitude) if profile.latitude is not None else None,
                longitude=float(profile.longitude) if profile.longitude is not None else None,
                rating=float(profile.rating) if profile.rating is not None else 0,
                verified=profile.verified,
            )
            for _, user, profile in results
        ]
    
    # جستجوی عمومی
    results = await search_service.search_technicians(
        db,
        query=search or "",
        category=category,
        city=city,
        verified_only=True
    )
    
    out = []
    for user, profile in results:
        item = TechnicianOut(
            id=user.id,
            full_name=user.full_name,
            business_name=profile.business_name,
            category=profile.category,
            city=profile.city,
            address=profile.address,
            latitude=float(profile.latitude) if profile.latitude is not None else None,
            longitude=float(profile.longitude) if profile.longitude is not None else None,
            rating=float(profile.rating) if profile.rating is not None else 0,
            verified=profile.verified,
        )
        out.append(item)
    
    return out


@router.get("/search", summary="جستجوی پیشرفته")
async def advanced_search(
    q: str = Query(..., min_length=2, description="عبارت جستجو"),
    type: str = Query("all", regex="^(all|technicians|ads)$", description="نوع جستجو"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    جستجوی پیشرفته در تکنسین‌ها و آگهی‌ها
    """
    results = {}
    
    if type in ["all", "technicians"]:
        tech_results = await search_service.search_technicians(
            db,
            query=q,
            category=category,
            city=city
        )
        results["technicians"] = [
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "business_name": profile.business_name,
                "category": profile.category,
                "city": profile.city,
                "rating": float(profile.rating) if profile.rating else 0,
            }
            for user, profile in tech_results
        ]
    
    if type in ["all", "ads"]:
        ad_results = await search_service.search_ads(
            db,
            query=q,
            category=category,
            city=city
        )
        results["ads"] = [
            {
                "id": str(ad.id),
                "title": ad.title,
                "description": ad.description[:100] + "...",
                "category": ad.category,
                "city": ad.city,
            }
            for ad in ad_results
        ]
    
    return results
