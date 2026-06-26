import os
import re
import time
import asyncio

from typing import List, Dict

import httpx
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv(override=True)

# ==========================================
# CONFIGURATION
# ==========================================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

MAX_RESULTS_YOUTUBE = 5
MAX_RESULTS_GOOGLE = 8

PLATFORM_COLORS = {
    "youtube": "#FF0000",
    "google": "#4285F4",
    "meta": "#1877F2"
}

STOP_WORDS = {
    "the","and","for","with","this","that",
    "nike","official","video","youtube",
    "watch","from","your","their","into",
    "have","more","than","using","latest",
    "shop","new","our","you","they","his",
    "her","its"
}

def remove_duplicates(items: list[dict]) -> list[dict]:

    seen = set()
    cleaned = []

    for item in items:

        url = item.get("url")

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)
        cleaned.append(item)

    return cleaned

# ==========================================
# EXTRACT KEYWORDS
# ==========================================

def extract_keywords(text: str):

    if not text:
        return []

    words = re.findall(r"[A-Za-z]{4,}", text.lower())

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        keywords.append(word)

    freq = {}

    for word in keywords:
        freq[word] = freq.get(word, 0) + 1

    return sorted(freq, key=freq.get, reverse=True)[:10]


# ==========================================
# PLATFORM SCORE
# ==========================================

# ==========================================
# RELEVANCE SCORING
# ==========================================

def calculate_score(item, brand_name):

    score = 0

    brand = brand_name.lower()

    platform = item.get("platform", "").lower()

    title = item.get("title", "").lower()

    description = item.get("description", "").lower()

    metadata = item.get("metadata", {})

    channel = metadata.get("channel", "").lower()

    # Platform weight
    if platform == "youtube":
        score += 30

    elif platform == "google":
        score += 25

    elif platform == "meta":
        score += 20

    # Brand relevance
    if brand in title:
        score += 30

    if brand in description:
        score += 15

    if brand in channel:
        score += 20

    # Advertisement keywords
    keywords = [
        "official",
        "commercial",
        "advertisement",
        "campaign",
        "launch",
        "promo",
        "ad"
    ]

    for word in keywords:

        if word in title:
            score += 10

        if word in description:
            score += 5

    return score
# ==========================================
# YOUTUBE FETCHER
# ==========================================

async def fetch_youtube_ads(brand_name: str):

    if not YOUTUBE_API_KEY:
        print("DEBUG: Missing YouTube API Key")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": f"{brand_name} commercial",
        "type": "video",
        "order": "relevance",
        "maxResults": MAX_RESULTS_YOUTUBE,
        "key": YOUTUBE_API_KEY
    }
    try:

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(url, params=params)

            response.raise_for_status()

            data = response.json()

        videos = []

        for item in data.get("items", []):

            snippet = item["snippet"]

            video_id = item["id"]["videoId"]

            description = snippet.get("description", "")

            combined_text = (
                snippet.get("title", "")
                + " "
                + description
            )

            keywords = extract_keywords(combined_text)

            video = {

                "id": video_id,

                "platform": "youtube",

                "platform_color": PLATFORM_COLORS["youtube"],

                "ad_type": "video",

                "title": snippet.get("title"),

                "description": description,

                "url": f"https://www.youtube.com/watch?v={video_id}",

                "thumbnail": snippet["thumbnails"]["high"]["url"],

                "keywords": keywords,

                "score": 0,

                "metadata": {

                    "channel": snippet.get("channelTitle"),

                    "published_at": snippet.get("publishedAt"),

                    "language": snippet.get("defaultLanguage"),

                    "channel_id": snippet.get("channelId")

                }

            }

            video["score"] = calculate_score(
                video,
                brand_name
            )

            videos.append(video)

        videos.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print(f"DEBUG: YouTube returned {len(videos)} items")

        return videos

    except httpx.HTTPStatusError as e:

        print("YouTube HTTP Error")

        print(e.response.status_code)

        print(e.response.text)

        return []

    except Exception:

        import traceback

        print("\n========== YOUTUBE ERROR ==========")

        traceback.print_exc()

        print("==================================\n")

        return []
    
# ==========================================
# GOOGLE FETCHER
# ==========================================

async def fetch_google_ads(brand_name: str):

    if not SERPAPI_API_KEY:
        print("DEBUG: Missing SerpAPI Key")
        return []

    try:

        params = {
            "engine": "google",
            "q": f"{brand_name} official advertisement campaign",
            "num": MAX_RESULTS_GOOGLE,
            "api_key": SERPAPI_API_KEY
        }

        search = GoogleSearch(params)

        results = search.get_dict()

        if "error" in results:
            print("SerpAPI Error:", results["error"])
            return []

        google_results = []

        blacklist = [
            "wikipedia",
            "dictionary",
            "britannica"
        ]

        for item in results.get("organic_results", []):

            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            lower = (
                title + " " + snippet + " " + link
            ).lower()

            if any(word in lower for word in blacklist):
                continue

            combined_text = title + " " + snippet

            keywords = extract_keywords(combined_text)

            result = {

                "id": item.get("position"),

                "platform": "google",

                "platform_color": PLATFORM_COLORS["google"],

                "ad_type": "search",

                "title": title,

                "description": snippet,

                "url": link,

                "thumbnail": item.get("thumbnail"),

                "keywords": keywords,

                "score": 0,

                "metadata": {

                    "displayed_link": item.get("displayed_link"),

                    "source": item.get("source"),

                    "favicon": item.get("favicon")

                }

            }

            result["score"] = calculate_score(
                result,
                brand_name
            )

            google_results.append(result)

        google_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print(
            f"DEBUG: Google returned {len(google_results)} items"
        )

        return google_results

    except Exception:

        import traceback

        print("\n========== GOOGLE ERROR ==========")

        traceback.print_exc()

        print("=================================\n")

        return []
# ==========================================
# META FETCHER (GRACEFUL FALLBACK)
# ==========================================

async def fetch_meta_ads(brand_name: str):

    if not META_ACCESS_TOKEN:

        print("DEBUG: Meta token missing")

        return []

    try:

        url = "https://graph.facebook.com/v23.0/ads_archive"

        params = {
            "search_terms": brand_name,
            "ad_reached_countries": '["IN"]',
            "ad_type": "ALL",
            "fields": "id,page_name,ad_creation_time",
            "access_token": META_ACCESS_TOKEN
        }

        async with httpx.AsyncClient(timeout=15) as client:

            response = await client.get(url, params=params)

        if response.status_code != 200:

            print("Meta unavailable:")
            print(response.text)

            return []

        data = response.json()

        ads = []

        for item in data.get("data", []):

            ads.append({

                "id": item.get("id"),

                "platform": "meta",

                "platform_color": PLATFORM_COLORS["meta"],

                "ad_type": "social",

                "title": item.get("page_name"),

                "description": "",

                "url": "",

                "thumbnail": None,

                "keywords": [],

                "score": 25,

                "metadata": {

                    "created": item.get("ad_creation_time")

                }

            })

        return ads

    except Exception as e:

        print("Meta Error:", e)

        return []



# ==========================================
# MAIN DISCOVERY ENGINE
# ==========================================

async def unified_ad_discovery(
    brand_name: str,
    platform: str = None,
    ad_type: str = None,
    sort_by: str = "score"
):

    start_time = time.time()

    fetchers = {}

    if platform is None or platform.lower() == "youtube":
        fetchers["youtube"] = fetch_youtube_ads(brand_name)

    if platform is None or platform.lower() == "google":
        fetchers["google"] = fetch_google_ads(brand_name)

    if platform is None or platform.lower() == "meta":
        fetchers["meta"] = fetch_meta_ads(brand_name)

    results = await asyncio.gather(
        *fetchers.values(),
        return_exceptions=True
    )

    gallery = []
    outages = []

    summary = {
        "youtube": 0,
        "google": 0,
        "meta": 0
    }

    # -----------------------------------------
    # MERGE RESULTS
    # -----------------------------------------

    for platform_name, result in zip(fetchers.keys(), results):

        if isinstance(result, Exception):

            print(f"{platform_name} failed: {result}")
            outages.append(platform_name)
            continue

        if not isinstance(result, list):

            outages.append(platform_name)
            continue

        print(f"{platform_name} returned {len(result)} items")

        for item in result:

            if ad_type:

                if item.get("ad_type", "").lower() != ad_type.lower():
                    continue

            gallery.append(item)

            if platform_name in summary:
                summary[platform_name] = len(result)

    # -----------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------

    gallery = remove_duplicates(gallery)

    # -----------------------------------------
    # SORT
    # -----------------------------------------

    if sort_by == "title":

        gallery.sort(
            key=lambda x: x.get("title", "")
        )

    elif sort_by == "date":

        gallery.sort(
            key=lambda x: x.get("metadata", {}).get("published_at", ""),
            reverse=True
        )

    elif sort_by == "score":

        gallery.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

    # -----------------------------------------
    # STATUS
    # -----------------------------------------

    if len(outages) == 0:
        status = "success"
    elif len(outages) == len(fetchers):
        status = "failed"
    else:
        status = "partial_success"

    execution_time = round(
        (time.time() - start_time) * 1000,
        2
    )

    # -----------------------------------------
    # RESPONSE
    # -----------------------------------------

    return {

        "status": status,

        "query": brand_name,

        "execution_time_ms": execution_time,

        "summary": summary,

        "outages_logged": outages,

        "count": len(gallery),

        "gallery": gallery

    }



# ==========================================
# BUILD GPT PROMPT
# ==========================================

def build_ai_prompt(brand_name: str, ai_summary: dict):

    keywords = ", ".join(ai_summary.get("keywords", []))

    campaigns = "\n".join(
        f"- {c}" for c in ai_summary.get("campaigns", [])
    )

    prompt = f"""
You are an expert digital marketing strategist.

Brand:
{brand_name}

Popular Campaigns:
{campaigns}

Important Keywords:
{keywords}

Generate a professional advertising campaign.

Return ONLY valid JSON.

Format:

{{
    "headline":"",
    "caption":"",
    "cta":"",
    "hashtags":[
        "",
        "",
        ""
    ],
    "banner_prompt":"",
    "target_audience":"",
    "tone":""
}}

Requirements:

- Headline should be catchy.
- Caption should be 40-80 words.
- CTA should be short.
- Banner prompt should describe an image suitable for AI image generation.
- Tone should match the brand.
"""

    return prompt

# ==========================================
# AI PAYLOAD
# ==========================================

def build_ai_payload(brand_name, gallery):

    summary = build_brand_summary(
        brand_name,
        gallery
    )

    prompt = build_ai_prompt(
        brand_name,
        summary
    )

    return {

        "brand": brand_name,

        "summary": summary,

        "prompt": prompt

    }
