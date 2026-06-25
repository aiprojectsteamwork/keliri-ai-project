from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.branch_repository import BranchRepository
from app.repositories.offer_repository import OfferRepository
from app.schemas.schemas import ActiveOfferSummary, LocationRequest, NearestBranchResponse
from app.utils.haversine import haversine


class LocationService:
    def __init__(self, db: Session):
        self.branch_repo = BranchRepository(db)
        self.offer_repo = OfferRepository(db)

    # ------------------------------------------------------------------
    def find_nearest_branch(self, location: LocationRequest) -> NearestBranchResponse:
        branches = self.branch_repo.list_active()
        if not branches:
            raise NotFoundError("Branch", "any active")

        # O(n) scan — acceptable for hundreds of branches; switch to PostGIS for thousands
        nearest = None
        min_dist = float("inf")
        for branch in branches:
            dist = haversine(
                location.latitude,
                location.longitude,
                float(branch.latitude),
                float(branch.longitude),
            )
            if dist < min_dist:
                min_dist = dist
                nearest = branch

        # Fetch active offer for the nearest branch
        active_offer: Optional[ActiveOfferSummary] = None
        offer = self.offer_repo.get_active_for_branch(nearest.id)
        if offer:
            active_offer = ActiveOfferSummary(
                id=offer.id,
                title=offer.title,
                discount_percentage=float(offer.discount_percentage) if offer.discount_percentage else None,
                end_date=offer.end_date,
            )

        return NearestBranchResponse(
            branch_id=nearest.id,
            branch_name=nearest.branch_name,
            distance_km=min_dist,
            address=nearest.address,
            city=nearest.city,
            latitude=float(nearest.latitude),
            longitude=float(nearest.longitude),
            active_offer=active_offer,
        )
