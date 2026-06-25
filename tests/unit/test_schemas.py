"""Unit tests for Pydantic schema validation."""
import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.schemas.schemas import (
    BrandCreate,
    BranchCreate,
    OfferCreate,
    LocationRequest,
    PaginationParams,
)


class TestBrandCreate:
    def test_valid(self):
        b = BrandCreate(name="Haldiram's", slug="haldirams")
        assert b.slug == "haldirams"

    def test_slug_must_be_lowercase_hyphen(self):
        with pytest.raises(ValidationError):
            BrandCreate(name="X", slug="Has Spaces")

    def test_slug_no_uppercase(self):
        with pytest.raises(ValidationError):
            BrandCreate(name="X", slug="MyBrand")

    def test_name_cannot_be_empty(self):
        with pytest.raises(ValidationError):
            BrandCreate(name="", slug="ok-slug")


class TestBranchCreate:
    def _base(self, **kw):
        defaults = dict(
            brand_id=1,
            branch_name="Test Branch",
            latitude=12.9716,
            longitude=77.5946,
            address="100 Main St",
            city="Bengaluru",
            state="Karnataka",
        )
        return BranchCreate(**{**defaults, **kw})

    def test_valid(self):
        b = self._base()
        assert b.city == "Bengaluru"

    def test_latitude_out_of_range(self):
        with pytest.raises(ValidationError):
            self._base(latitude=91.0)

    def test_longitude_out_of_range(self):
        with pytest.raises(ValidationError):
            self._base(longitude=-181.0)

    def test_default_country(self):
        b = self._base()
        assert b.country == "India"


class TestOfferCreate:
    def _base(self, **kw):
        today = date.today()
        defaults = dict(
            branch_id=1,
            title="50% OFF",
            start_date=today,
            end_date=today + timedelta(days=30),
        )
        return OfferCreate(**{**defaults, **kw})

    def test_valid(self):
        o = self._base()
        assert o.title == "50% OFF"

    def test_end_before_start_raises(self):
        today = date.today()
        with pytest.raises(ValidationError):
            self._base(start_date=today + timedelta(days=10), end_date=today)

    def test_discount_over_100_raises(self):
        with pytest.raises(ValidationError):
            self._base(discount_percentage=101.0)

    def test_valid_days_deduped_and_sorted(self):
        o = self._base(valid_days=[0, 0, 6, 1])
        assert o.valid_days == [0, 1, 6]

    def test_valid_days_out_of_range(self):
        with pytest.raises(ValidationError):
            self._base(valid_days=[7])


class TestLocationRequest:
    def test_valid(self):
        loc = LocationRequest(latitude=12.839, longitude=77.677)
        assert loc.latitude == 12.839

    def test_invalid_latitude(self):
        with pytest.raises(ValidationError):
            LocationRequest(latitude=95.0, longitude=0.0)

    def test_invalid_longitude(self):
        with pytest.raises(ValidationError):
            LocationRequest(latitude=0.0, longitude=200.0)


class TestPaginationParams:
    def test_offset_calculation(self):
        p = PaginationParams(page=3, page_size=10)
        assert p.offset == 20

    def test_page_size_max(self):
        with pytest.raises(ValidationError):
            PaginationParams(page=1, page_size=101)
