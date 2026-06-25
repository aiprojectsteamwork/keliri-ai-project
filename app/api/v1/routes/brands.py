from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.schemas import BrandCreate, BrandOut, BrandUpdate, Page, PaginationParams
from app.services.brand_service import BrandService

router = APIRouter(prefix="/brands", tags=["Brands"])


def _svc(db: Session = Depends(get_db)) -> BrandService:
    return BrandService(db)


@router.post("", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
def create_brand(data: BrandCreate, svc: BrandService = Depends(_svc)):
    return svc.create(data)


@router.get("", response_model=Page[BrandOut])
def list_brands(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    sort_by: str = Query("id", pattern=r"^(id|name|created_at)$"),
    sort_dir: str = Query("asc", pattern=r"^(asc|desc)$"),
    svc: BrandService = Depends(_svc),
):
    return svc.list(
        PaginationParams(page=page, page_size=page_size),
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(brand_id: int, svc: BrandService = Depends(_svc)):
    return svc.get(brand_id)


@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(brand_id: int, data: BrandUpdate, svc: BrandService = Depends(_svc)):
    return svc.update(brand_id, data)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(brand_id: int, svc: BrandService = Depends(_svc)):
    svc.delete(brand_id)
