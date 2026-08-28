from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

def now(): return datetime.now(timezone.utc)

class Role(str, Enum):
    GENERAL = "general"
    TECHNICIAN = "technician"
    ADMIN = "admin"

class AdStatus(str, Enum):
    DRAFT="draft"; PENDING_PAYMENT="pending_payment"; PENDING_REVIEW="pending_review"; ACTIVE="active"; REJECTED="rejected"; EXPIRED="expired"; SUSPENDED="suspended"

class PaymentStatus(str, Enum):
    PENDING="pending"; PAID="paid"; FAILED="failed"; REFUNDED="refunded"

class User(Base):
    __tablename__="users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str|None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[Role] = mapped_column(String(20), default=Role.GENERAL, index=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    profile: Mapped["TechnicianProfile|None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ads: Mapped[list["Advertisement"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class TechnicianProfile(Base):
    __tablename__="technician_profiles"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    business_name: Mapped[str] = mapped_column(String(160))
    bio: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80), index=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    address: Mapped[str] = mapped_column(String(300), default="")
    latitude: Mapped[float|None] = mapped_column(Numeric(10,7), nullable=True)
    longitude: Mapped[float|None] = mapped_column(Numeric(10,7), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rating: Mapped[float] = mapped_column(Numeric(3,2), default=0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    user: Mapped[User] = relationship(back_populates="profile")

class SubscriptionPlan(Base):
    __tablename__="subscription_plans"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    duration_days: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(18,2))
    currency: Mapped[str] = mapped_column(String(5), default="IRR")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Subscription(Base):
    __tablename__="subscriptions"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("subscription_plans.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    user: Mapped[User] = relationship(back_populates="subscriptions")
    plan: Mapped[SubscriptionPlan] = relationship()

class AdPlan(Base):
    __tablename__="ad_plans"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    duration_days: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(18,2))
    currency: Mapped[str] = mapped_column(String(5), default="IRR")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Advertisement(Base):
    __tablename__="advertisements"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), index=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[float|None] = mapped_column(Numeric(10,7), nullable=True)
    longitude: Mapped[float|None] = mapped_column(Numeric(10,7), nullable=True)
    status: Mapped[AdStatus] = mapped_column(String(30), default=AdStatus.DRAFT, index=True)
    plan_id: Mapped[UUID|None] = mapped_column(ForeignKey("ad_plans.id"), nullable=True)
    starts_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    owner: Mapped[User] = relationship(back_populates="ads")
    plan: Mapped[AdPlan|None] = relationship()
    __table_args__=(Index("ix_ads_public", "status", "category", "city"),)

class Payment(Base):
    __tablename__="payments"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(30))
    reference: Mapped[str] = mapped_column(String(120), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18,2))
    currency: Mapped[str] = mapped_column(String(5))
    status: Mapped[PaymentStatus] = mapped_column(String(20), default=PaymentStatus.PENDING, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    paid_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__=(UniqueConstraint("user_id","reference",name="uq_payment_reference"),)

class Conversation(Base):
    __tablename__="conversations"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    technician_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Message(Base):
    __tablename__="messages"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
