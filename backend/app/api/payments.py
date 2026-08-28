from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.payments import PaymentService

router=APIRouter(prefix="/payments",tags=["payments"])

@router.post("/callback")
async def callback(reference:str,db:AsyncSession=Depends(get_db)):
    payment=await PaymentService().confirm(db,reference)
    if not payment: raise HTTPException(404,"Payment not found")
    return {"reference":payment.reference,"status":payment.status.value}
