from typing import List, Optional

# Distance thresholds (meters) for early lane positioning warnings
_WARN_HEAVY_TRAFFIC = 2000   # warn this far out when traffic is heavy
_WARN_NORMAL        = 1000   # warn this far out under normal conditions
_CRITICAL           = 400    # must be in correct lane by this point


def lane_advice_from_maneuver(instruction: str) -> str:
    """Return a short lane positioning directive for a single maneuver instruction."""
    ins = instruction.lower()
    if "left" in ins:
        return "Favor LEFT lanes early"
    if "right" in ins:
        return "Favor RIGHT lanes early"
    if "u-turn" in ins or "uturn" in ins:
        return "Prepare for U-turn lane/median access"
    return "Stay flexible; prepare to choose lane soon"


def _maneuver_direction(instruction: str) -> Optional[str]:
    """Return 'left', 'right', 'uturn', or None."""
    ins = instruction.lower()
    if "u-turn" in ins or "uturn" in ins:
        return "uturn"
    if "left" in ins:
        return "left"
    if "right" in ins:
        return "right"
    return None


def urgency(distance_meters: int, traffic_heavy: bool) -> str:
    """
    Classify how urgently the driver needs to act.

    Returns HIGH (≤400m), MEDIUM (within warning threshold), or LOW.
    Warning thresholds: 2000m when traffic is heavy, 1000m otherwise.
    """
    threshold = _WARN_HEAVY_TRAFFIC if traffic_heavy else _WARN_NORMAL
    if distance_meters <= _CRITICAL:
        return "HIGH"
    if distance_meters <= threshold:
        return "MEDIUM"
    return "LOW"


def lookahead_advice(
    current_step_index: int,
    steps: List[dict],
    traffic_heavy: bool,
) -> Optional[str]:
    """
    Look ahead from current_step_index to find the next directional maneuver.
    Returns a proactive positioning message if the driver should start moving
    into the correct lane now, based on cumulative distance and traffic.

    Returns None if no early action is needed yet.
    """
    warn_threshold = _WARN_HEAVY_TRAFFIC if traffic_heavy else _WARN_NORMAL

    # Cumulative distance from the end of the current step onward
    cumulative_dist = 0
    steps_ahead = 0

    for i in range(current_step_index + 1, len(steps)):
        step = steps[i]
        dist_m = int(step.get("distanceMeters", 0) or 0)
        instruction = format_instruction(step)
        direction = _maneuver_direction(instruction)

        if direction:
            # This is an upcoming turn/maneuver
            steps_ahead = i - current_step_index

            if cumulative_dist <= warn_threshold:
                # Driver should already be positioning
                traffic_note = "with the current traffic, " if traffic_heavy else ""
                steps_label = (
                    "at the next signal"
                    if steps_ahead == 1
                    else f"in about {steps_ahead} signals"
                )

                if direction == "left":
                    lane_dir = "LEFT"
                elif direction == "right":
                    lane_dir = "RIGHT"
                else:
                    lane_dir = "U-TURN"

                urgency_level = urgency(cumulative_dist, traffic_heavy)

                if urgency_level == "HIGH":
                    return (
                        f"Get into the {lane_dir} lane NOW — "
                        f"you need to turn {direction} {steps_label}."
                    )
                else:
                    return (
                        f"Heads up: {traffic_note}start moving to the {lane_dir} lanes — "
                        f"you'll need to turn {direction} {steps_label}."
                    )

            # Found a directional maneuver but it's far enough away; no warning yet
            return None

        cumulative_dist += dist_m

    return None


def format_instruction(step: dict) -> str:
    """Extract a human-readable instruction string from a Routes API step."""
    ni = step.get("navigationInstruction", {})
    if "instructions" in ni:
        return ni["instructions"]
    return step.get("maneuver", "Continue")
