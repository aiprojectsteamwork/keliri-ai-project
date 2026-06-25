"""
API integration tests.
Uses the TestClient fixture (SQLite in-memory) from conftest.py.
"""
import pytest
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------
class TestBrandsAPI:
    def test_create_brand(self, client):
        r = client.post("/api/v1/brands", json={"name": "Haldiram's", "slug": "haldirams"})
        assert r.status_code == 201
        data = r.json()
        assert data["slug"] == "haldirams"
        assert "id" in data

    def test_create_duplicate_slug_returns_409(self, client):
        payload = {"name": "A", "slug": "unique-slug"}
        client.post("/api/v1/brands", json=payload)
        r = client.post("/api/v1/brands", json=payload)
        assert r.status_code == 409

    def test_list_brands_pagination(self, client):
        for i in range(5):
            client.post("/api/v1/brands", json={"name": f"Brand {i}", "slug": f"brand-{i}"})
        r = client.get("/api/v1/brands?page=1&page_size=3")
        assert r.status_code == 200
        body = r.json()
        assert len(body["items"]) <= 3
        assert body["meta"]["page"] == 1

    def test_get_brand_not_found(self, client):
        r = client.get("/api/v1/brands/9999")
        assert r.status_code == 404

    def test_update_brand(self, client):
        r = client.post("/api/v1/brands", json={"name": "Old", "slug": "update-me"})
        brand_id = r.json()["id"]
        r2 = client.put(f"/api/v1/brands/{brand_id}", json={"name": "New Name"})
        assert r2.status_code == 200
        assert r2.json()["name"] == "New Name"

    def test_delete_brand(self, client):
        r = client.post("/api/v1/brands", json={"name": "Del", "slug": "delete-me"})
        brand_id = r.json()["id"]
        r2 = client.delete(f"/api/v1/brands/{brand_id}")
        assert r2.status_code == 204
        r3 = client.get(f"/api/v1/brands/{brand_id}")
        assert r3.status_code == 404

    def test_invalid_slug_format(self, client):
        r = client.post("/api/v1/brands", json={"name": "X", "slug": "Has Spaces!"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------
class TestBranchesAPI:
    def _create_brand(self, client, slug="test-brand"):
        r = client.post("/api/v1/brands", json={"name": "Test Brand", "slug": slug})
        return r.json()["id"]

    def _branch_payload(self, brand_id):
        return {
            "brand_id": brand_id,
            "branch_name": "Electronic City",
            "latitude": 12.8399,
            "longitude": 77.6770,
            "address": "Hosur Rd, Electronic City",
            "city": "Bengaluru",
            "state": "Karnataka",
        }

    def test_create_branch(self, client):
        brand_id = self._create_brand(client, "branch-brand-1")
        r = client.post("/api/v1/branches", json=self._branch_payload(brand_id))
        assert r.status_code == 201
        assert r.json()["branch_name"] == "Electronic City"

    def test_list_branches_filter_by_city(self, client):
        brand_id = self._create_brand(client, "branch-brand-2")
        client.post("/api/v1/branches", json=self._branch_payload(brand_id))
        r = client.get("/api/v1/branches?city=Bengaluru")
        assert r.status_code == 200
        for branch in r.json()["items"]:
            assert "Bengaluru" in branch["city"] or "bengaluru" in branch["city"].lower()

    def test_get_branch_by_id(self, client):
        brand_id = self._create_brand(client, "branch-brand-3")
        created = client.post("/api/v1/branches", json=self._branch_payload(brand_id)).json()
        r = client.get(f"/api/v1/branches/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_update_branch(self, client):
        brand_id = self._create_brand(client, "branch-brand-4")
        branch_id = client.post("/api/v1/branches", json=self._branch_payload(brand_id)).json()["id"]
        r = client.put(f"/api/v1/branches/{branch_id}", json={"branch_name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["branch_name"] == "Updated Name"

    def test_delete_branch(self, client):
        brand_id = self._create_brand(client, "branch-brand-5")
        branch_id = client.post("/api/v1/branches", json=self._branch_payload(brand_id)).json()["id"]
        assert client.delete(f"/api/v1/branches/{branch_id}").status_code == 204
        assert client.get(f"/api/v1/branches/{branch_id}").status_code == 404

    def test_invalid_latitude(self, client):
        brand_id = self._create_brand(client, "branch-brand-6")
        payload = self._branch_payload(brand_id)
        payload["latitude"] = 999
        r = client.post("/api/v1/branches", json=payload)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Offers
# ---------------------------------------------------------------------------
class TestOffersAPI:
    def _setup(self, client):
        brand_id = client.post("/api/v1/brands", json={"name": "OfferCo", "slug": f"offerco-{id(client)}"}).json()["id"]
        branch_payload = {
            "brand_id": brand_id,
            "branch_name": "Offer Branch",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "address": "5th Block",
            "city": "Bengaluru",
            "state": "Karnataka",
        }
        branch_id = client.post("/api/v1/branches", json=branch_payload).json()["id"]
        return branch_id

    def _offer_payload(self, branch_id):
        today = date.today()
        return {
            "branch_id": branch_id,
            "title": "50% OFF Sweets",
            "discount_percentage": 50.0,
            "start_date": str(today),
            "end_date": str(today + timedelta(days=30)),
            "valid_days": [0, 1, 2, 3, 4, 5, 6],
        }

    def test_create_offer(self, client):
        branch_id = self._setup(client)
        r = client.post("/api/v1/offers", json=self._offer_payload(branch_id))
        assert r.status_code == 201
        assert r.json()["title"] == "50% OFF Sweets"

    def test_list_active_offers(self, client):
        branch_id = self._setup(client)
        client.post("/api/v1/offers", json=self._offer_payload(branch_id))
        r = client.get("/api/v1/offers/active")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_active_offers_filter_by_branch(self, client):
        branch_id = self._setup(client)
        client.post("/api/v1/offers", json=self._offer_payload(branch_id))
        r = client.get(f"/api/v1/offers/active?branch_id={branch_id}")
        assert r.status_code == 200
        for offer in r.json():
            assert offer["branch_id"] == branch_id

    def test_offer_invalid_dates(self, client):
        branch_id = self._setup(client)
        today = date.today()
        payload = self._offer_payload(branch_id)
        payload["start_date"] = str(today + timedelta(days=10))
        payload["end_date"] = str(today)
        r = client.post("/api/v1/offers", json=payload)
        assert r.status_code == 422

    def test_update_offer(self, client):
        branch_id = self._setup(client)
        offer_id = client.post("/api/v1/offers", json=self._offer_payload(branch_id)).json()["id"]
        r = client.put(f"/api/v1/offers/{offer_id}", json={"title": "New Title"})
        assert r.status_code == 200
        assert r.json()["title"] == "New Title"


# ---------------------------------------------------------------------------
# Location / Nearest Branch
# ---------------------------------------------------------------------------
class TestNearestBranchAPI:
    def _seed(self, client):
        brand_id = client.post("/api/v1/brands", json={"name": "GeoTest", "slug": "geo-test-brand"}).json()["id"]
        branches = [
            {"name": "Electronic City", "lat": 12.8399, "lon": 77.6770},
            {"name": "Koramangala",     "lat": 12.9352, "lon": 77.6245},
            {"name": "Indiranagar",     "lat": 12.9784, "lon": 77.6408},
        ]
        for b in branches:
            client.post(
                "/api/v1/branches",
                json={
                    "brand_id": brand_id,
                    "branch_name": b["name"],
                    "latitude": b["lat"],
                    "longitude": b["lon"],
                    "address": "Test Address",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                },
            )

    def test_nearest_branch_returns_closest(self, client):
        self._seed(client)
        # Query point is right next to Electronic City
        r = client.post("/api/v1/nearest-branch", json={"latitude": 12.840, "longitude": 77.677})
        assert r.status_code == 200
        body = r.json()
        assert body["branch_name"] == "Electronic City"
        assert body["distance_km"] < 2.0

    def test_nearest_branch_response_shape(self, client):
        self._seed(client)
        r = client.post("/api/v1/nearest-branch", json={"latitude": 12.9352, "longitude": 77.6245})
        assert r.status_code == 200
        body = r.json()
        assert "branch_id" in body
        assert "branch_name" in body
        assert "distance_km" in body
        assert "active_offer" in body

    def test_nearest_branch_invalid_coordinates(self, client):
        r = client.post("/api/v1/nearest-branch", json={"latitude": 200.0, "longitude": 77.6})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
