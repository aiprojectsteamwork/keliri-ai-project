from __future__ import annotations
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.models import Branch
from app.repositories.branch_repository import BranchRepository
from app.schemas.schemas import BranchCreate, BranchUpdate, Page, PageMeta, PaginationParams


class BranchService:
    def __init__(self, db: Session):
        self.repo = BranchRepository(db)

    # ------------------------------------------------------------------
    def create(self, data: BranchCreate) -> Branch:
        return self.repo.create(data)

    def get(self, branch_id: int) -> Branch:
        branch = self.repo.get_by_id(branch_id)
        if not branch:
            raise NotFoundError("Branch", branch_id)
        return branch

    def list(
        self,
        pagination: PaginationParams,
        *,
        brand_id=None,
        city=None,
        is_active=None,
        search=None,
        sort_by="id",
        sort_dir="asc",
    ) -> Page:
        items, total = self.repo.list(
            brand_id=brand_id,
            city=city,
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

    def update(self, branch_id: int, data: BranchUpdate) -> Branch:
        branch = self.get(branch_id)
        return self.repo.update(branch, data)

    def delete(self, branch_id: int) -> None:
        branch = self.get(branch_id)
        self.repo.soft_delete(branch)
