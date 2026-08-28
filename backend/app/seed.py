import asyncio
from sqlalchemy import select
from app.core.db import SessionLocal
from app.core.config import settings
from app.core.security import hash_password
from app.models import User,Role,SubscriptionPlan,AdPlan

async def main():
 async with SessionLocal() as db:
  if not await db.scalar(select(User).where(User.phone==settings.admin_phone)):
   db.add(User(phone=settings.admin_phone,password_hash=hash_password(settings.admin_password),full_name="GANDOM Admin",role=Role.ADMIN,phone_verified=True))
  subs=[("روزانه","day",1), ("هفتگی","week",7),("ماهانه","month",30),("سالانه","year",365)]
  for name,slug,days in subs:
   if not await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.slug==slug)): db.add(SubscriptionPlan(name=name,slug=slug,duration_days=days,price=0,currency=settings.default_currency))
  ads=[("۱ روزه","ad-day",1),("۱ هفته","ad-week",7),("۱ ماه","ad-month",30),("۱ سال","ad-year",365)]
  for name,slug,days in ads:
   if not await db.scalar(select(AdPlan).where(AdPlan.slug==slug)): db.add(AdPlan(name=name,slug=slug,duration_days=days,price=0,currency=settings.default_currency))
  await db.commit()
if __name__=="__main__": asyncio.run(main())
