from datetime import datetime, timezone, timedelta
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Advertisement, AdPlan, AdStatus, User, TechnicianProfile

async def expire_ads(db: AsyncSession):
    now=datetime.now(timezone.utc)
    rows=(await db.execute(select(Advertisement).where(Advertisement.status==AdStatus.ACTIVE, Advertisement.ends_at<=now))).scalars().all()
    for ad in rows: ad.status=AdStatus.EXPIRED
    if rows: await db.commit()

async def public_ads(db: AsyncSession, category=None, city=None):
    await expire_ads(db)
    now=datetime.now(timezone.utc)
    q=select(Advertisement).where(Advertisement.status==AdStatus.ACTIVE, Advertisement.starts_at<=now, Advertisement.ends_at>now)
    if category: q=q.where(Advertisement.category==category)
    if city: q=q.where(Advertisement.city==city)
    q=q.order_by(Advertisement.created_at.desc()).limit(100)
    return (await db.execute(q)).scalars().all()
