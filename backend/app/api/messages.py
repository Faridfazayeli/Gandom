from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.deps import verified_user
from app.models import User, TechnicianProfile, Conversation, Message
from app.schemas import MessageIn, MessageOut

router=APIRouter(prefix="/messages",tags=["messages"])

@router.post("",response_model=MessageOut)
async def send(data:MessageIn,user:User=Depends(verified_user),db:AsyncSession=Depends(get_db)):
    tech=await db.scalar(select(User).join(TechnicianProfile).where(User.id==data.technician_id,User.role=="technician",User.is_active.is_(True)))
    if not tech: raise HTTPException(404,"Technician not found")
    convo=await db.scalar(select(Conversation).where(or_(and_(Conversation.sender_id==user.id,Conversation.technician_id==tech.id),and_(Conversation.sender_id==tech.id,Conversation.technician_id==user.id))))
    if not convo: convo=Conversation(sender_id=user.id,technician_id=tech.id); db.add(convo); await db.flush()
    msg=Message(conversation_id=convo.id,sender_id=user.id,body=data.body); db.add(msg); await db.commit(); await db.refresh(msg); return msg
