from fastapi import FastAPI
from app.models import RouteAdviceRequest, RouteAdviceResponse, ManeuverAdvice
from app.services.google_routes import compute_route, to_waypoint
from app.services.lane_strategy import lane_advice_from_maneuver, urgency, format_instruction

app = FastAPI(title="Lane Strategy Assistant", version="0.1.0")

@app.post("/route-advice", response_model=RouteAdviceResponse)
async def route_advice(req: RouteAdviceRequest):
    origin = to_waypoint(req.origin if isinstance(req.origin, str) else req.origin.model_dump())
    dest = to_waypoint(req.destination if isinstance(req.destination, str) else req.destination.model_dump())

    data = await compute_route(origin, dest, req.travel_mode)

    routes = data.get("routes", [])
    if not routes:
        return RouteAdviceResponse(eta_seconds=0, maneuvers=[], raw=data)

    route = routes[0]
    base_eta = _parse_duration_seconds(route.get("duration"))
    # traffic advisory may include "speedReadingIntervals" etc depending on mask; keep simple
    traffic_eta = None

    # Steps
    maneuvers = []
    legs = route.get("legs", [])
    if legs:
        steps = legs[0].get("steps", [])
        # pick first few maneuvers
        for s in steps[:3]:
            instruction = format_instruction(s)
            dist_m = int(s.get("distanceMeters", 0) or 0)

            # crude traffic signal: if routingPreference is traffic aware, assume "heavy" when close to maneuver
            traffic_heavy = dist_m <= 1600  # v0 placeholder; we’ll replace with better signal later
            u = urgency(dist_m, traffic_heavy)

            advice = lane_advice_from_maneuver(instruction)
            if u == "HIGH":
                advice = advice.replace("early", "NOW")

            maneuvers.append(ManeuverAdvice(
                instruction=instruction,
                distance_meters=dist_m,
                lane_advice=advice,
                urgency=u
            ))

    return RouteAdviceResponse(
        eta_seconds=base_eta,
        eta_with_traffic_seconds=traffic_eta,
        maneuvers=maneuvers,
        raw=data
    )

def _parse_duration_seconds(d: str | None) -> int:
    # Routes API duration often like "123s"
    if not d:
        return 0
    if isinstance(d, str) and d.endswith("s"):
        try:
            return int(float(d[:-1]))
        except:
            return 0
    return 0