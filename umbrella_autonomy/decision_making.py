"""Decision-making helpers for Umbrella autonomy."""

from typing import Any, Dict


class DecisionEngine:
    """Simple decision engine scaffold."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def assess_situation(self, sensors: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sensor input and current state."""
        peaks = [float(sensors.get(f"peak{i}", 0.0) or 0.0) for i in range(1, 4)]
        rms_values = [float(sensors.get(f"rms{i}", 0.0) or 0.0) for i in range(1, 4)]
        max_peak = max(peaks) if peaks else 0.0
        mean_rms = sum(rms_values) / len(rms_values) if rms_values else 0.0

        elevated_threshold = float(self.config.get("elevated_threshold", 0.18))
        active_threshold = float(self.config.get("active_threshold", 0.35))

        if max_peak >= active_threshold:
            status = "active"
            recommendation = "record"
            confidence = min(0.98, 0.6 + max_peak)
        elif max_peak >= elevated_threshold or mean_rms >= elevated_threshold / 2:
            status = "elevated"
            recommendation = "monitor"
            confidence = min(0.9, 0.5 + max(mean_rms, max_peak) / 2)
        else:
            status = "nominal"
            recommendation = "hold"
            confidence = 0.78

        return {
            "status": status,
            "recommendation": recommendation,
            "confidence": round(confidence, 3),
            "peak": round(max_peak, 4),
            "rms": round(mean_rms, 4),
        }

    def choose_action(self, situation: Dict[str, Any]) -> str:
        """Choose an action based on the assessed situation."""
        recommendation = situation.get("recommendation")
        if recommendation == "move":
            return "navigate"
        if recommendation == "record":
            return "record"
        return "monitor"

    def update_state(self, state: Dict[str, Any], action: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update the autonomy state after taking an action."""
        new_state = state.copy()
        new_state["last_action"] = action
        new_state["feedback"] = feedback
        return new_state
