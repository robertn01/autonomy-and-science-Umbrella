"""Basic navigation utilities for Umbrella autonomy."""

from typing import Dict, List, Tuple

class NavigationSystem:
    """Simple navigation system scaffold."""

    def __init__(self, map_data: Dict = None):
        self.map_data = map_data or {}

    def plan_path(self, start: Tuple[float, float], goal: Tuple[float, float], obstacles: List[Tuple[float, float]] = None) -> List[Tuple[float, float]]:
        """Return a simple straight-line path for now."""
        if obstacles:
            # TODO: integrate obstacle avoidance
            pass
        return [start, goal]

    def estimate_eta(self, path: List[Tuple[float, float]], speed: float = 1.0) -> float:
        """Estimate travel time along a path."""
        if len(path) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(path)):
            dx = path[i][0] - path[i-1][0]
            dy = path[i][1] - path[i-1][1]
            total += (dx ** 2 + dy ** 2) ** 0.5
        return total / speed
