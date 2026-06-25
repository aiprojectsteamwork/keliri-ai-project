from __future__ import annotations
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.models import Offer
from app.repositories.offer_repository import OfferRepository
from app.schemas.schemas import OfferCreate, OfferUpdate, Page, PageMeta, PaginationParams


class OfferService:
    def __init__(self, db: Session):
        self.repo = OfferRepository(db)

    # ------------------------------------------------------------------
    def create(self, data: OfferCreate) -> Offer:
        return self.repo.create(data)

    def get(self, offer_id: int) -> Offer:
        offer = self.repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundError("Offer", offer_id)
        return offer

    def list(
        self,
        pagination: PaginationParams,
        *,
        branch_id=None,
        campaign_id=None,
        is_active=None,
        sort_by="id",
        sort_dir="asc",
    ) -> Page:
        items, total = self.repo.list(
            branch_id=branch_id,
            campaign_id=campaign_id,
            is_active=is_active,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        return Page(
            items=items,
            meta=PageMeta(
                page=pagination.page,
                page_size=pagination.page_size,
                total=total,
                total_pages=max(1, -(-total // pagination.page_size)),
            ),
        )

    def list_active(self, branch_id=None) -> List[Offer]:
        return self.repo.list_active_today(branch_id=branch_id)

    def update(self, offer_id: int, data: OfferUpdate) -> Offer:
        offer = self.get(offer_id)
        return self.repo.update(offer, data)

    def delete(self, offer_id: int) -> None:
        offer = self.get(offer_id)
        self.repo.soft_delete(offer)
