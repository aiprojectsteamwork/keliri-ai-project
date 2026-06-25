"""
Pydantic v2 schemas — request/response validation for all resources.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Generic pagination wrapper
# ---------------------------------------------------------------------------
T = TypeVar("T")


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class Page(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class BrandOut(BrandBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------
class BranchBase(BaseModel):
    brand_id: int
    branch_name: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(default="India", max_length=100)
    pincode: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    branch_name: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class BranchOut(BranchBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------
class CampaignBase(BaseModel):
    brand_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    start_date: date
    end_date: date
    status: str = Field(default="draft", pattern=r"^(draft|active|paused|completed|cancelled)$")

    @model_validator(mode="after")
    def validate_dates(self) -> "CampaignBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern=r"^(draft|active|paused|completed|cancelled)$")


class CampaignOut(CampaignBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Offer
# ---------------------------------------------------------------------------
class OfferBase(BaseModel):
    branch_id: int
    campaign_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    start_date: date
    end_date: date
    valid_days: List[int] = Field(
        default=[0, 1, 2, 3, 4, 5, 6],
        description="0=Sun … 6=Sat",
    )
    is_active: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "OfferBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self

    @field_validator("valid_days")
    @classmethod
    def validate_valid_days(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("valid_days cannot be empty")
        if not all(0 <= d <= 6 for d in v):
            raise ValueError("valid_days values must be 0–6")
        return sorted(set(v))


class OfferCreate(OfferBase):
    pass


class OfferUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    valid_days: Optional[List[int]] = None
    is_active: Optional[bool] = None


class OfferOut(OfferBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Location / Nearest-branch
# ---------------------------------------------------------------------------
class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, examples=[12.839])
    longitude: float = Field(..., ge=-180, le=180, examples=[77.677])


class ActiveOfferSummary(BaseModel):
    id: int
    title: str
    discount_percentage: Optional[float]
    end_date: date


class NearestBranchResponse(BaseModel):
    branch_id: int
    branch_name: str
    distance_km: float
    address: str
    city: str
    latitude: float
    longitude: float
    active_offer: Optional[ActiveOfferSummary] = None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
class AnalyticsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    advertisement_id: int
    branch_id: int
    date: date
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    updated_at: datetime


# ---------------------------------------------------------------------------
# Shared query params
# ---------------------------------------------------------------------------
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
