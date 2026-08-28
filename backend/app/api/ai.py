from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.deps import verified_user
from app.models import User
from app.services.repair_ai import RepairAI

router=APIRouter(prefix="/ai",tags=["repair-ai"])
class DiagnoseIn(BaseModel): symptom:str=Field(min_length=3,max_length=4000); category:str|None=None
@router.post("/diagnose")
async def diagnose(data:DiagnoseIn,user:User=Depends(verified_user)):
    r=RepairAI().diagnose(data.symptom,data.category)
    return {"title":r.title,"confidence":r.confidence,"risk":r.risk,"steps":r.steps,"safety":r.safety}
