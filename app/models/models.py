"""
SQLAlchemy ORM models — mirrors the PostgreSQL schema exactly.
"""
from __future__ import annotations

import uuid as _uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


# ---------------------------------------------------------------------------
# Mixin helpers
# ---------------------------------------------------------------------------
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
class Brand(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "brands"

    id        = Column(Integer, primary_key=True, index=True)
    uuid      = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    name      = Column(String(255), nullable=False)
    slug      = Column(String(255), unique=True, nullable=False)
    logo_url  = Column(Text)
    website   = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    # relationships
    branches  = relationship("Branch",   back_populates="brand", lazy="select")
    campaigns = relationship("Campaign", back_populates="brand", lazy="select")
    assets    = relationship("Asset",    back_populates="brand", lazy="select")


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------
class Branch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "branches"
    __table_args__ = (
        CheckConstraint("latitude  BETWEEN -90  AND 90",  name="chk_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="chk_longitude"),
        Index("idx_branches_geo", "latitude", "longitude"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    uuid        = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    brand_id    = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_name = Column(String(255), nullable=False)
    latitude    = Column(Numeric(10, 7), nullable=False)
    longitude   = Column(Numeric(10, 7), nullable=False)
    address     = Column(Text, nullable=False)
    city        = Column(String(100), nullable=False)
    state       = Column(String(100), nullable=False)
    country     = Column(String(100), default="India", nullable=False)
    pincode     = Column(String(20))
    phone       = Column(String(30))
    email       = Column(String(255))
    is_active   = Column(Boolean, default=True, nullable=False)

    # relationships
    brand         = relationship("Brand",         back_populates="branches")
    offers        = relationship("Offer",         back_populates="branch",  lazy="select")
    advertisements = relationship("Advertisement", back_populates="branch", lazy="select")


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------
class Campaign(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_campaign_dates"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    uuid        = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    brand_id    = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    description = Column(Text)
    budget      = Column(Numeric(12, 2))
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    status      = Column(
        String(20),
        CheckConstraint("status IN ('draft','active','paused','completed','cancelled')"),
        default="draft",
        nullable=False,
        index=True,
    )

    brand          = relationship("Brand",         back_populates="campaigns")
    offers         = relationship("Offer",         back_populates="campaign", lazy="select")
    advertisements = relationship("Advertisement", back_populates="campaign", lazy="select")


# ---------------------------------------------------------------------------
# Offer
# ---------------------------------------------------------------------------
class Offer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "offers"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_offer_dates"),
        CheckConstraint("discount_percentage BETWEEN 0 AND 100", name="chk_discount"),
    )

    id                  = Column(Integer, primary_key=True, index=True)
    uuid                = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    branch_id           = Column(Integer, ForeignKey("branches.id",  ondelete="CASCADE"),  nullable=False, index=True)
    campaign_id         = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True,  index=True)
    title               = Column(String(255), nullable=False)
    description         = Column(Text)
    discount_percentage = Column(Numeric(5, 2))
    start_date          = Column(Date, nullable=False)
    end_date            = Column(Date, nullable=False)
    valid_days          = Column(ARRAY(Integer), default=list, nullable=False)
    is_active           = Column(Boolean, default=True, nullable=False)

    branch   = relationship("Branch",   back_populates="offers")
    campaign = relationship("Campaign", back_populates="offers")


# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------
class Asset(Base, SoftDeleteMixin):
    __tablename__ = "assets"

    id           = Column(Integer, primary_key=True, index=True)
    uuid         = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    brand_id     = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name    = Column(String(255), nullable=False)
    file_url     = Column(Text, nullable=False)
    file_type    = Column(String(50), nullable=False)
    file_size_kb = Column(Integer)
    width_px     = Column(Integer)
    height_px    = Column(Integer)
    created_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    brand          = relationship("Brand",         back_populates="assets")
    advertisements = relationship("Advertisement", back_populates="asset", lazy="select")


# ---------------------------------------------------------------------------
# Advertisement
# ---------------------------------------------------------------------------
class Advertisement(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "advertisements"

    id          = Column(Integer, primary_key=True, index=True)
    uuid        = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"),  nullable=False, index=True)
    branch_id   = Column(Integer, ForeignKey("branches.id",  ondelete="CASCADE"),  nullable=False, index=True)
    offer_id    = Column(Integer, ForeignKey("offers.id",    ondelete="SET NULL"),  nullable=True)
    asset_id    = Column(Integer, ForeignKey("assets.id",    ondelete="SET NULL"),  nullable=True)
    title       = Column(String(255), nullable=False)
    body_text   = Column(Text)
    cta_label   = Column(String(100), default="Learn More")
    cta_url     = Column(Text)
    format      = Column(
        String(30),
        CheckConstraint("format IN ('banner','interstitial','native','video')"),
        default="banner",
        nullable=False,
    )
    radius_km   = Column(Numeric(6, 2), default=5.0, nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)

    campaign    = relationship("Campaign", back_populates="advertisements")
    branch      = relationship("Branch",   back_populates="advertisements")
    offer       = relationship("Offer",    lazy="joined")
    asset       = relationship("Asset",    back_populates="advertisements")
    impressions = relationship("Impression", back_populates="advertisement", lazy="select")


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id        = Column(Integer, primary_key=True, index=True)
    uuid      = Column(UUID(as_uuid=True), default=_uuid.uuid4, unique=True, nullable=False)
    device_id = Column(String(255), unique=True)
    email     = Column(String(255), unique=True)
    phone     = Column(String(30))
    name      = Column(String(255))
    city      = Column(String(100))
    state     = Column(String(100))
    country   = Column(String(100), default="India")
    is_active = Column(Boolean, default=True, nullable=False)


# ---------------------------------------------------------------------------
# Impression
# ---------------------------------------------------------------------------
class Impression(Base):
    __tablename__ = "impressions"

    id               = Column(BigInteger, primary_key=True, index=True)
    advertisement_id = Column(Integer, ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id          = Column(Integer, ForeignKey("users.id",          ondelete="SET NULL"), nullable=True,  index=True)
    branch_id        = Column(Integer, ForeignKey("branches.id",       ondelete="CASCADE"), nullable=False, index=True)
    user_latitude    = Column(Numeric(10, 7))
    user_longitude   = Column(Numeric(10, 7))
    distance_km      = Column(Numeric(8, 3))
    device_type      = Column(String(50))
    ip_address       = Column(INET)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    advertisement = relationship("Advertisement", back_populates="impressions")


# ---------------------------------------------------------------------------
# Click
# ---------------------------------------------------------------------------
class Click(Base):
    __tablename__ = "clicks"

    id               = Column(BigInteger, primary_key=True, index=True)
    impression_id    = Column(BigInteger, ForeignKey("impressions.id", ondelete="CASCADE"), nullable=False, index=True)
    advertisement_id = Column(Integer,    ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id          = Column(Integer,    ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    cta_url          = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------
class Conversion(Base):
    __tablename__ = "conversions"
    __table_args__ = (
        CheckConstraint(
            "conversion_type IN ('visit','purchase','signup','call')",
            name="chk_conversion_type",
        ),
    )

    id               = Column(BigInteger, primary_key=True, index=True)
    click_id         = Column(BigInteger, ForeignKey("clicks.id", ondelete="SET NULL"), nullable=True)
    advertisement_id = Column(Integer, ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id          = Column(Integer, ForeignKey("users.id",          ondelete="SET NULL"), nullable=True)
    branch_id        = Column(Integer, ForeignKey("branches.id",       ondelete="CASCADE"), nullable=False, index=True)
    conversion_type  = Column(String(50), default="visit", nullable=False)
    revenue          = Column(Numeric(12, 2))
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


# ---------------------------------------------------------------------------
# Analytics (daily roll-up)
# ---------------------------------------------------------------------------
class Analytics(Base):
    __tablename__ = "analytics"
    __table_args__ = (
        UniqueConstraint("advertisement_id", "branch_id", "date", name="uq_analytics_ad_branch_date"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    advertisement_id = Column(Integer, ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id        = Column(Integer, ForeignKey("branches.id",       ondelete="CASCADE"), nullable=False, index=True)
    date             = Column(Date, nullable=False, index=True)
    impressions      = Column(Integer, default=0, nullable=False)
    clicks           = Column(Integer, default=0, nullable=False)
    conversions      = Column(Integer, default=0, nullable=False)
    revenue          = Column(Numeric(12, 2), default=0, nullable=False)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
