import httpx
from typing import Dict, Any
from app.core.config import GOOGLE_MAPS_API_KEY

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

async def compute_route(origin: dict, destination: dict, travel_mode: str = "DRIVE") -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        # Field mask keeps costs and payload small. Expand later.
        "X-Goog-FieldMask": "routes.duration,routes.travelAdvisory,routes.legs.steps",
    }

    body = {
        "origin": origin,
        "destination": destination,
        "travelMode": travel_mode,
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",  # traffic-aware routing :contentReference[oaicite:6]{index=6}
        "computeAlternativeRoutes": False,
        "languageCode": "en-US",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(ROUTES_URL, headers=headers, json=body)
        r.raise_for_status()
        return r.json()

def to_waypoint(value):
    """
    Accepts:
      - {"lat":..., "lng":...} dict
      - "address string"
    """
    if isinstance(value, dict) and "lat" in value and "lng" in value:
        return {"location": {"latLng": {"latitude": value["lat"], "longitude": value["lng"]}}}
    if isinstance(value, str):
        return {"address": value}
    raise ValueError("origin/destination must be an address string or {lat,lng} dict")