from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LatLng(BaseModel):
    lat: float
    lng: float

class RouteAdviceRequest(BaseModel):
    origin: str | LatLng
    destination: str | LatLng
    current_position: Optional[LatLng] = None
    travel_mode: str = Field(default="DRIVE")  # Routes API: DRIVE, WALK, BICYCLE, etc.

class ManeuverAdvice(BaseModel):
    instruction: str
    distance_meters: int
    lane_advice: str
    urgency: str
    lookahead_advice: Optional[str] = None

class RouteAdviceResponse(BaseModel):
    eta_seconds: int
    eta_with_traffic_seconds: Optional[int] = None
    maneuvers: List[ManeuverAdvice]
    raw: Optional[Dict[str, Any]] = None