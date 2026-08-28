from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.core.security import decode_token
from app.models import User, Role

bearer = HTTPBearer(auto_error=False)

async def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: AsyncSession = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status_code=401, detail="Authentication required")
    try: payload = decode_token(credentials.credentials)
    except Exception: raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "access": raise HTTPException(status_code=401, detail="Access token required")
    user = await db.get(User, payload.get("sub"))
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="User unavailable")
    return user

async def verified_user(user: User = Depends(current_user)) -> User:
    if not user.phone_verified: raise HTTPException(status_code=403, detail="Phone verification required")
    return user

async def technician(user: User = Depends(verified_user), db: AsyncSession = Depends(get_db)) -> User:
    if user.role != Role.TECHNICIAN: raise HTTPException(status_code=403, detail="Technician role required")
    from app.services.entitlement import technician_access
    if not await technician_access(db, user.id): raise HTTPException(status_code=402, detail="Active technician subscription and verified profile required")
    return user

async def admin(user: User = Depends(current_user)) -> User:
    if user.role != Role.ADMIN: raise HTTPException(status_code=403, detail="Admin only")
    return user
