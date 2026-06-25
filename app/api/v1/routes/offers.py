from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.schemas import OfferCreate, OfferOut, OfferUpdate, Page, PaginationParams
from app.services.offer_service import OfferService

router = APIRouter(prefix="/offers", tags=["Offers"])


def _svc(db: Session = Depends(get_db)) -> OfferService:
    return OfferService(db)


@router.post("", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def create_offer(data: OfferCreate, svc: OfferService = Depends(_svc)):
    return svc.create(data)


@router.get("", response_model=Page[OfferOut])
def list_offers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    branch_id: Optional[int] = Query(None),
    campaign_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query("id", pattern=r"^(id|title|start_date|end_date)$"),
    sort_dir: str = Query("asc", pattern=r"^(asc|desc)$"),
    svc: OfferService = Depends(_svc),
):
    return svc.list(
        PaginationParams(page=page, page_size=page_size),
        branch_id=branch_id,
        campaign_id=campaign_id,
        is_active=is_active,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/active", response_model=List[OfferOut])
def list_active_offers(
    branch_id: Optional[int] = Query(None),
    svc: OfferService = Depends(_svc),
):
    """Returns all offers that are active and valid today."""
    return svc.list_active(branch_id=branch_id)


@router.get("/{offer_id}", response_model=OfferOut)
def get_offer(offer_id: int, svc: OfferService = Depends(_svc)):
    return svc.get(offer_id)


@router.put("/{offer_id}", response_model=OfferOut)
def update_offer(offer_id: int, data: OfferUpdate, svc: OfferService = Depends(_svc)):
    return svc.update(offer_id, data)


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(offer_id: int, svc: OfferService = Depends(_svc)):
    svc.delete(offer_id)
