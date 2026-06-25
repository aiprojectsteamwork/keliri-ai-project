import os
import sys
import asyncio

# Automatically tell Python to look in the root folder for the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now your import will work perfectly
from app.services.discovery_services import unified_ad_discovery

async def test():
    print("Starting Aggregator Engine...")
    results = await unified_ad_discovery("Nike")
    print(f"Fetched {results['count']} items successfully!")
    if results['gallery']:
        print("First item preview:", results['gallery'][0])
    else:
        print("No results found. Double-check your API keys or fallback status.")

if __name__ == "__main__":
    asyncio.run(test())