# Lane Strategy Assistant

A navigation enhancement that gives proactive lane-positioning advice based on upcoming turns and traffic conditions — so you never miss a turn because you were in the wrong lane.

## The Problem

Google Maps tells you to "turn left in 200m" when you're already stuck in the right lane in heavy traffic. This tool watches your upcoming route and warns you early: *"Heads up: with the current traffic, start moving to the LEFT lanes — you'll need to turn left in about 2 signals."*

## Setup

**Requirements:** Python 3.11+, a [Google Maps Platform](https://developers.google.com/maps) API key with the Routes API enabled.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
GOOGLE_MAPS_API_KEY=your_key_here
```

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API

### `POST /route-advice`

Returns ETA and per-step lane positioning advice for a route.

**Request**
```json
{
  "origin": "1600 Amphitheatre Parkway, Mountain View, CA",
  "destination": "1 Infinite Loop, Cupertino, CA",
  "travel_mode": "DRIVE"
}
```

`origin` and `destination` accept either an address string or a `{ "lat": float, "lng": float }` object.

**Response**
```json
{
  "eta_seconds": 1847,
  "eta_with_traffic_seconds": null,
  "maneuvers": [
    {
      "instruction": "Head south on Amphitheatre Pkwy",
      "distance_meters": 320,
      "lane_advice": "Stay flexible; prepare to choose lane soon",
      "urgency": "HIGH",
      "lookahead_advice": "Heads up: with the current traffic, start moving to the LEFT lanes — you'll need to turn left at the next signal."
    },
    {
      "instruction": "Turn left onto Charleston Rd",
      "distance_meters": 980,
      "lane_advice": "Favor LEFT lanes NOW",
      "urgency": "MEDIUM",
      "lookahead_advice": null
    }
  ],
  "raw": {}
}
```

**Fields**

| Field | Description |
|---|---|
| `urgency` | `HIGH` / `MEDIUM` / `LOW` — how soon you need to act |
| `lane_advice` | Advice for the current step's own maneuver |
| `lookahead_advice` | Proactive warning based on upcoming turns (null if no action needed yet) |

**Urgency thresholds**

| Condition | MEDIUM from | HIGH from |
|---|---|---|
| Normal traffic | 1000m | 400m |
| Heavy traffic | 2000m | 400m |
