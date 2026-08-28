from fastapi import APIRouter
from app.core.db import engine
from sqlalchemy import text
router=APIRouter(tags=["health"])
@router.get("/health")
async def health():
    async with engine.connect() as c: await c.execute(text("SELECT 1"))
    return {"status":"ok"}
