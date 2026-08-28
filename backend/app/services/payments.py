from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Payment, PaymentStatus, Subscription, SubscriptionPlan, Advertisement, AdPlan, AdStatus

class PaymentService:
    async def create(self, db: AsyncSession, user_id, purpose: str, amount, currency: str, metadata: dict):
        ref = f"GND-{uuid4().hex.upper()}"
        payment = Payment(user_id=user_id, purpose=purpose, reference=ref, amount=amount, currency=currency, metadata_json=metadata)
        db.add(payment); await db.commit(); await db.refresh(payment)
        return payment

    async def confirm(self, db: AsyncSession, reference: str):
        payment = await db.scalar(__import__('sqlalchemy').select(Payment).where(Payment.reference==reference).with_for_update())
        if not payment: return None
        if payment.status == PaymentStatus.PAID: return payment
        payment.status=PaymentStatus.PAID; payment.paid_at=datetime.now(timezone.utc)
        meta=payment.metadata_json or {}
        if payment.purpose == "subscription":
            plan=await db.get(SubscriptionPlan, meta["plan_id"])
            now=datetime.now(timezone.utc)
            db.add(Subscription(user_id=payment.user_id, plan_id=plan.id, starts_at=now, ends_at=now+timedelta(days=plan.duration_days), active=True))
        elif payment.purpose == "ad":
            ad=await db.get(Advertisement, meta["ad_id"]); plan=await db.get(AdPlan, meta["plan_id"])
            ad.status=AdStatus.PENDING_REVIEW
            ad.plan_id=plan.id
        await db.commit(); await db.refresh(payment); return payment
