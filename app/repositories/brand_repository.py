from __future__ import annotations
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Brand
from app.schemas.schemas import BrandCreate, BrandUpdate


class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def _active(self):
        return self.db.query(Brand).filter(Brand.deleted_at.is_(None))

    # ------------------------------------------------------------------
    def create(self, data: BrandCreate) -> Brand:
        brand = Brand(**data.model_dump())
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def get_by_id(self, brand_id: int) -> Optional[Brand]:
        return self._active().filter(Brand.id == brand_id).first()

    def get_by_slug(self, slug: str) -> Optional[Brand]:
        return self._active().filter(Brand.slug == slug).first()

    def list(
        self,
        *,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "id",
        sort_dir: str = "asc",
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Brand], int]:
        q = self._active()
        if is_active is not None:
            q = q.filter(Brand.is_active == is_active)
        if search:
            q = q.filter(Brand.name.ilike(f"%{search}%"))

        total = q.with_entities(func.count()).scalar()

        col = getattr(Brand, sort_by, Brand.id)
        q = q.order_by(col.desc() if sort_dir == "desc" else col.asc())
        return q.offset(offset).limit(limit).all(), total

    def update(self, brand: Brand, data: BrandUpdate) -> Brand:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(brand, field, value)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def soft_delete(self, brand: Brand) -> Brand:
        from datetime import datetime, timezone
        brand.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return brand
