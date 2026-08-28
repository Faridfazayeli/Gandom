from typing import Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Advertisement, TechnicianProfile, User, AdStatus
from datetime import datetime, timezone


class SearchService:
    """Advanced search service for technicians and advertisements."""
    
    async def search_technicians(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        city: Optional[str] = None,
        verified_only: bool = True,
        limit: int = 50
    ):
        """Search for technicians by name, business name, or category."""
        q = select(User, TechnicianProfile).join(TechnicianProfile)
        
        if verified_only:
            q = q.where(TechnicianProfile.verified.is_(True))
        
        filters = [
            User.is_active.is_(True),
            User.role == "technician",
        ]
        
        if query:
            filters.append(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    TechnicianProfile.business_name.ilike(f"%{query}%"),
                    TechnicianProfile.bio.ilike(f"%{query}%"),
                )
            )
        
        if category:
            filters.append(TechnicianProfile.category == category)
        
        if city:
            filters.append(TechnicianProfile.city == city)
        
        q = q.where(and_(*filters)).limit(limit)
        
        return (await db.execute(q)).all()
    
    async def search_ads(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        category: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 100
    ):
        """Search for active advertisements."""
        now = datetime.now(timezone.utc)
        
        filters = [
            Advertisement.status == AdStatus.ACTIVE,
            Advertisement.starts_at <= now,
            Advertisement.ends_at > now,
        ]
        
        if query:
            filters.append(
                or_(
                    Advertisement.title.ilike(f"%{query}%"),
                    Advertisement.description.ilike(f"%{query}%"),
                )
            )
        
        if category:
            filters.append(Advertisement.category == category)
        
        if city:
            filters.append(Advertisement.city == city)
        
        q = select(Advertisement).where(and_(*filters)).order_by(Advertisement.created_at.desc()).limit(limit)
        
        return (await db.execute(q)).scalars().all()
    
    async def search_by_location(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        category: Optional[str] = None,
        limit: int = 50
    ):
        """Search for technicians within radius using Haversine formula."""
        from math import radians, sin, cos, asin, sqrt
        
        def distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in km."""
            p = radians(1)
            lat1, lon1, lat2, lon2 = lat1*p, lon1*p, lat2*p, lon2*p
            x = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
            return 6371 * 2 * asin(sqrt(x))
        
        q = select(User, TechnicianProfile).join(TechnicianProfile).where(
            User.is_active.is_(True),
            User.role == "technician",
            TechnicianProfile.verified.is_(True),
            TechnicianProfile.latitude.isnot(None),
            TechnicianProfile.longitude.isnot(None),
        )
        
        if category:
            q = q.where(TechnicianProfile.category == category)
        
        rows = (await db.execute(q)).all()
        
        results = []
        for user, profile in rows:
            if profile.latitude is not None and profile.longitude is not None:
                dist = distance(latitude, longitude, float(profile.latitude), float(profile.longitude))
                if dist <= radius_km:
                    results.append((dist, user, profile))
        
        results.sort(key=lambda x: x[0])
        return results[:limit]
