from fastapi import APIRouter, Query, HTTPException
from app.services.discovery_services import unified_ad_discovery

# This variable name must be exactly 'router'
router = APIRouter(prefix="/ad-discovery", tags=["Ad Discovery"])

@router.get("/")
async def get_discovered_ads(
    brand_name: str = Query(..., description="Name of the brand"),
    platform: str = Query(None, description="Filter by platform (youtube, google, meta)"),
    ad_type: str = Query(None, description="Filter by ad type (video, image, text)"),
    sort_by: str = Query(None, description="Sort options (most_recent, most_viewed)")
):
    try:
        results = await unified_ad_discovery(
            brand_name=brand_name, 
            platform=platform, 
            ad_type=ad_type, 
            sort_by=sort_by
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
