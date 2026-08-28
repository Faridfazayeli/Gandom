from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class RegisterIn(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    role: str = "general"

class LoginIn(BaseModel):
    phone: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ProfileIn(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    bio: str = ""
    category: str = Field(min_length=2, max_length=80)
    city: str = Field(min_length=2, max_length=100)
    address: str = ""
    latitude: float|None = None
    longitude: float|None = None

class AdCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=5000)
    category: str = Field(min_length=2, max_length=80)
    city: str = Field(min_length=2, max_length=100)
    latitude: float|None = None
    longitude: float|None = None
    plan_id: UUID

class AdOut(BaseModel):
    id: UUID; title: str; description: str; category: str; city: str; status: str; owner_id: UUID; starts_at: datetime|None; ends_at: datetime|None; views: int
    model_config = {"from_attributes": True}

class PlanOut(BaseModel):
    id: UUID; name: str; slug: str; duration_days: int; price: Decimal; currency: str
    model_config = {"from_attributes": True}

class TechnicianOut(BaseModel):
    id: UUID; full_name: str; business_name: str; category: str; city: str; address: str; latitude: float|None; longitude: float|None; rating: float; verified: bool

class MessageIn(BaseModel):
    technician_id: UUID
    body: str = Field(min_length=1, max_length=4000)

class MessageOut(BaseModel):
    id: UUID; conversation_id: UUID; sender_id: UUID; body: str; created_at: datetime
    model_config = {"from_attributes": True}
