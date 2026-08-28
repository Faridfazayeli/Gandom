from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.deps import verified_user
from app.models import SubscriptionPlan, User
from app.services.payments import PaymentService
from app.schemas import PlanOut

router=APIRouter(prefix="/subscriptions",tags=["subscriptions"])

@router.get("/plans",response_model=list[PlanOut])
async def plans(db:AsyncSession=Depends(get_db)): return (await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.active.is_(True)).order_by(SubscriptionPlan.duration_days))).scalars().all()

@router.post("/purchase/{plan_id}")
async def purchase(plan_id,user:User=Depends(verified_user),db:AsyncSession=Depends(get_db)):
    plan=await db.get(SubscriptionPlan,plan_id)
    if not plan or not plan.active: raise HTTPException(404,"Plan not found")
    p=await PaymentService().create(db,user.id,"subscription",plan.price,plan.currency,{"plan_id":str(plan.id)})
    return {"payment_reference":p.reference,"amount":str(p.amount),"status":"pending","next":"Send the reference to the configured payment gateway and return to callback."}
