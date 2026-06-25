from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.schemas import LocationRequest, NearestBranchResponse
from app.services.location_service import LocationService

router = APIRouter(tags=["Location Intelligence"])


def _svc(db: Session = Depends(get_db)) -> LocationService:
    return LocationService(db)


@router.post("/nearest-branch", response_model=NearestBranchResponse)
def nearest_branch(location: LocationRequest, svc: LocationService = Depends(_svc)):
    """
    Given a user's GPS coordinates, returns the nearest active branch
    along with its current active offer (if any).

    Example input:
    ```json
    { "latitude": 12.839, "longitude": 77.677 }
    ```
    """
    return svc.find_nearest_branch(location)
