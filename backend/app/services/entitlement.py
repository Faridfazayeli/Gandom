from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TechnicianProfile, Subscription

async def technician_access(db: AsyncSession, user_id):
    profile = (await db.execute(select(TechnicianProfile).where(TechnicianProfile.user_id==user_id, TechnicianProfile.verified.is_(True)))).scalar_one_or_none()
    if not profile: return False
    now = datetime.now(timezone.utc)
    sub = (await db.execute(select(Subscription).where(Subscription.user_id==user_id, Subscription.active.is_(True), Subscription.ends_at>now).order_by(Subscription.ends_at.desc()))).scalars().first()
    return sub is not None
