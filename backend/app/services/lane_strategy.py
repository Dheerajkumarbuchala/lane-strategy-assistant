from typing import Tuple

def lane_advice_from_maneuver(instruction: str) -> str:
    ins = instruction.lower()
    if "left" in ins:
        return "Favor LEFT lanes early"
    if "right" in ins:
        return "Favor RIGHT lanes early"
    if "u-turn" in ins or "uturn" in ins:
        return "Prepare for U-turn lane/median access"
    return "Stay flexible; prepare to choose lane soon"

def urgency(distance_meters: int, traffic_heavy: bool) -> str:
    # simple v0 heuristic; we’ll improve later
    if traffic_heavy and distance_meters <= 800:
        return "HIGH"
    if traffic_heavy and distance_meters <= 1600:
        return "MEDIUM"
    if distance_meters <= 600:
        return "MEDIUM"
    return "LOW"

def format_instruction(step: dict) -> str:
    # Routes steps include navigationInstruction in many cases, but field-mask is minimal.
    # We'll fall back to maneuver field if present.
    ni = step.get("navigationInstruction", {})
    if "instructions" in ni:
        return ni["instructions"]
    # fallback:
    return step.get("maneuver", "Continue")