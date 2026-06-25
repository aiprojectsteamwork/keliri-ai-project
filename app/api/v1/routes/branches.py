from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.schemas import BranchCreate, BranchOut, BranchUpdate, Page, PaginationParams
from app.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["Branches"])


def _svc(db: Session = Depends(get_db)) -> BranchService:
    return BranchService(db)


@router.post("", response_model=BranchOut, status_code=status.HTTP_201_CREATED)
def create_branch(data: BranchCreate, svc: BranchService = Depends(_svc)):
    return svc.create(data)


@router.get("", response_model=Page[BranchOut])
def list_branches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None, max_length=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    sort_by: str = Query("id", pattern=r"^(id|branch_name|city|created_at)$"),
    sort_dir: str = Query("asc", pattern=r"^(asc|desc)$"),
    svc: BranchService = Depends(_svc),
):
    return svc.list(
        PaginationParams(page=page, page_size=page_size),
        brand_id=brand_id,
        city=city,
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{branch_id}", response_model=BranchOut)
def get_branch(branch_id: int, svc: BranchService = Depends(_svc)):
    return svc.get(branch_id)


@router.put("/{branch_id}", response_model=BranchOut)
def update_branch(branch_id: int, data: BranchUpdate, svc: BranchService = Depends(_svc)):
    return svc.update(branch_id, data)


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(branch_id: int, svc: BranchService = Depends(_svc)):
    svc.delete(branch_id)
