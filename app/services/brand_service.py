from __future__ import annotations
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.models import Brand
from app.repositories.brand_repository import BrandRepository
from app.schemas.schemas import BrandCreate, BrandUpdate, Page, PageMeta, PaginationParams


class BrandService:
    def __init__(self, db: Session):
        self.repo = BrandRepository(db)

    # ------------------------------------------------------------------
    def create(self, data: BrandCreate) -> Brand:
        if self.repo.get_by_slug(data.slug):
            raise ConflictError(f"Brand slug '{data.slug}' already exists.")
        return self.repo.create(data)

    def get(self, brand_id: int) -> Brand:
        brand = self.repo.get_by_id(brand_id)
        if not brand:
            raise NotFoundError("Brand", brand_id)
        return brand

    def list(
        self,
        pagination: PaginationParams,
        *,
        is_active=None,
        search=None,
        sort_by="id",
        sort_dir="asc",
    ) -> Page:
        items, total = self.repo.list(
            is_active=is_active,
            search=search,
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

    def update(self, brand_id: int, data: BrandUpdate) -> Brand:
        brand = self.get(brand_id)
        return self.repo.update(brand, data)

    def delete(self, brand_id: int) -> None:
        brand = self.get(brand_id)
        self.repo.soft_delete(brand)
