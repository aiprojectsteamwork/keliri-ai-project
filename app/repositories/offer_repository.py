from __future__ import annotations
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Offer
from app.schemas.schemas import OfferCreate, OfferUpdate


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def _active(self):
        return self.db.query(Offer).filter(Offer.deleted_at.is_(None))

    # ------------------------------------------------------------------
    def create(self, data: OfferCreate) -> Offer:
        offer = Offer(**data.model_dump())
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        return self._active().filter(Offer.id == offer_id).first()

    def list(
        self,
        *,
        branch_id: Optional[int] = None,
        campaign_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "id",
        sort_dir: str = "asc",
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Offer], int]:
        q = self._active()
        if branch_id is not None:
            q = q.filter(Offer.branch_id == branch_id)
        if campaign_id is not None:
            q = q.filter(Offer.campaign_id == campaign_id)
        if is_active is not None:
            q = q.filter(Offer.is_active == is_active)

        total = q.with_entities(func.count()).scalar()
        col = getattr(Offer, sort_by, Offer.id)
        q = q.order_by(col.desc() if sort_dir == "desc" else col.asc())
        return q.offset(offset).limit(limit).all(), total

    def list_active_today(self, branch_id: Optional[int] = None) -> List[Offer]:
        today = date.today()
        q = (
            self._active()
            .filter(
                Offer.is_active.is_(True),
                Offer.start_date <= today,
                Offer.end_date >= today,
            )
        )
        if branch_id is not None:
            q = q.filter(Offer.branch_id == branch_id)
        return q.all()

    def get_active_for_branch(self, branch_id: int) -> Optional[Offer]:
        """Returns the first active offer valid today for a branch."""
        today = date.today()
        return (
            self._active()
            .filter(
                Offer.branch_id == branch_id,
                Offer.is_active.is_(True),
                Offer.start_date <= today,
                Offer.end_date >= today,
            )
            .first()
        )

    def update(self, offer: Offer, data: OfferUpdate) -> Offer:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(offer, field, value)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def soft_delete(self, offer: Offer) -> Offer:
        offer.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return offer
