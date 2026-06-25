import asyncio

# ==========================================
# FR-12: FILTERING AND SORTING UTILITY
# ==========================================
def apply_filters_and_sorting(gallery: list, platform: str = None, ad_type: str = None, sort_by: str = None):
    """Filters and sorts the aggregated gallery according to FR-12 requirements."""
    # 1. Apply Platform Filter
    if platform:
        gallery = [item for item in gallery if item["platform"].lower() == platform.lower()]
        
    # 2. Apply Ad Type Filter (video, image, text)
    if ad_type:
        gallery = [item for item in gallery if item["ad_type"].lower() == ad_type.lower()]
        
    # 3. Apply Sorting Rules
    if sort_by == "most_recent":
        gallery.sort(key=lambda x: x.get("metadata", {}).get("published_at", ""), reverse=True)
    elif sort_by == "most_viewed":
        gallery.sort(key=lambda x: x.get("metadata", {}).get("view_count", 0), reverse=True)
        
    return gallery


# ==========================================
# SIMULATED PLATFORM FETCHERS (SANDBOX FALLBACKS)
# ==========================================
async def fetch_meta_ads(brand_name: str):
    """Simulates extraction from Meta Ads Library Repository."""
    await asyncio.sleep(0.1)
    return [
        {
            "id": f"meta_{brand_name.lower()}_1",
            "platform": "meta",
            "ad_type": "image",
            "title": f"Official {brand_name} Seasonal Campaign Canvas",
            "source_url": "https://www.facebook.com/ads/library",
            "preview_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "metadata": {
                "published_at": "2026-06-20T10:00:00Z",
                "view_count": 12500
            }
        },
        {
            "id": f"meta_{brand_name.lower()}_2",
            "platform": "meta",
            "ad_type": "video",
            "title": f"{brand_name} Summer Blast Promo Video",
            "source_url": "https://www.facebook.com/ads/library",
            "preview_image": "https://images.unsplash.com/photo-1511556532299-8f662fc26c06",
            "metadata": {
                "published_at": "2026-06-24T15:30:00Z",
                "view_count": 45000
            }
        }
    ]

async def fetch_youtube_ads(brand_name: str):
    """Simulates extraction from YouTube Brand Index."""
    await asyncio.sleep(0.1)
    raise ValueError("YouTube API credentials missing or unauthenticated.")

async def fetch_google_ads(brand_name: str):
    """Simulates extraction from Google Display Network."""
    await asyncio.sleep(0.1)
    return [
        {
            "id": f"google_{brand_name.lower()}_1",
            "platform": "google",
            "ad_type": "text",
            "title": f"Shop the Latest {brand_name} Collection - Free Shipping",
            "source_url": "https://adstransparency.google.com",
            "preview_image": "",
            "metadata": {
                "published_at": "2026-06-18T08:15:00Z",
                "view_count": 3200
            }
        }
    ]


# ==========================================
# MAIN INTEGRATED PIPELINE ENGINE
# ==========================================
async def unified_ad_discovery(brand_name: str, platform: str = None, ad_type: str = None, sort_by: str = None):
    """
    Coordinating engine that extracts multi-platform media components 
    concurrently, logs operational outages, and filters outputs.
    """
    outages = []
    combined_gallery = []

    tasks = {
        "Meta": fetch_meta_ads(brand_name),
        "YouTube": fetch_youtube_ads(brand_name),
        "Google Banners": fetch_google_ads(brand_name)
    }

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    for platform_name, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            outages.append(platform_name)
        else:
            combined_gallery.extend(result)

    # Apply filters using the correct positional/keyword syntax matching the function signature
    filtered_gallery = apply_filters_and_sorting(
        gallery=combined_gallery, 
        platform=platform, 
        ad_type=ad_type, 
        sort_by=sort_by
    )

    return {
        "status": "success",
        "outages_logged": outages,
        "count": len(filtered_gallery),
        "gallery": filtered_gallery
    }