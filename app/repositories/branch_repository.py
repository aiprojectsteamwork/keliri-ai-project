from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Branch
from app.schemas.schemas import BranchCreate, BranchUpdate


class BranchRepository:
    def __init__(self, db: Session):
        self.db = db

    def _active(self):
        return self.db.query(Branch).filter(Branch.deleted_at.is_(None))

    # ------------------------------------------------------------------
    def create(self, data: BranchCreate) -> Branch:
        branch = Branch(**data.model_dump())
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)
        return branch

    def get_by_id(self, branch_id: int) -> Optional[Branch]:
        return self._active().filter(Branch.id == branch_id).first()

    def list(
        self,
        *,
        brand_id: Optional[int] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "id",
        sort_dir: str = "asc",
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Branch], int]:
        q = self._active()
        if brand_id is not None:
            q = q.filter(Branch.brand_id == brand_id)
        if city:
            q = q.filter(Branch.city.ilike(f"%{city}%"))
        if is_active is not None:
            q = q.filter(Branch.is_active == is_active)
        if search:
            q = q.filter(Branch.branch_name.ilike(f"%{search}%"))

        total = q.with_entities(func.count()).scalar()
        col = getattr(Branch, sort_by, Branch.id)
        q = q.order_by(col.desc() if sort_dir == "desc" else col.asc())
        return q.offset(offset).limit(limit).all(), total

    def list_active(self) -> List[Branch]:
        """Returns all active branches — used for Haversine scan."""
        return self._active().filter(Branch.is_active.is_(True)).all()

    def update(self, branch: Branch, data: BranchUpdate) -> Branch:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(branch, field, value)
        self.db.commit()
        self.db.refresh(branch)
        return branch

    def soft_delete(self, branch: Branch) -> Branch:
        branch.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return branch
