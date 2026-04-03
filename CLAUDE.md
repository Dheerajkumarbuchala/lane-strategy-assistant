# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Environment Setup

Create `backend/.env` with:
```
GOOGLE_MAPS_API_KEY=your_key_here
```

`config.py` loads this via `python-dotenv` and raises `RuntimeError` at startup if the key is missing.

## Architecture

This is a FastAPI backend + plain HTML/JS frontend for providing lane-change advice during navigation.

**Request flow:**
1. `POST /route-advice` in `main.py` receives origin/destination (address string or `{lat, lng}`)
2. `google_routes.py` calls the Google Routes API v2 (`computeRoutes`) with `TRAFFIC_AWARE_OPTIMAL` routing, returning only `routes.duration,routes.travelAdvisory,routes.legs.steps` via field mask
3. `lane_strategy.py` processes each step: `format_instruction()` extracts text, `urgency()` computes HIGH/MEDIUM/LOW based on distance and traffic flag, `lane_advice_from_maneuver()` returns directional lane guidance
4. Response returns ETA seconds + list of `ManeuverAdvice` objects (first 3 steps only, currently)

**Key design notes:**
- The traffic-heavy signal in `main.py` is a placeholder (`dist_m <= 1600`); it's intended to be replaced with real traffic data
- Only the first route and first leg are processed
- `to_waypoint()` in `google_routes.py` handles both address strings and lat/lng dicts for the Routes API format

**Models** (`models.py`): `RouteAdviceRequest`, `RouteAdviceResponse`, `ManeuverAdvice`, `LatLng` — all Pydantic v2.
