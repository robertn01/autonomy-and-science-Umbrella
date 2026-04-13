import numpy as np


class DecisionManager:
    def __init__(
        self,
        w_science=1.0,
        w_hazard=1.2,
        w_energy=0.8,
        w_return_penalty=0.8,
        w_visit_penalty=0.2,
        w_progress=0.8,
        low_energy_threshold=0.2
    ):
        self.w_science = w_science
        self.w_hazard = w_hazard
        self.w_energy = w_energy
        self.w_return_penalty = w_return_penalty
        self.w_visit_penalty = w_visit_penalty
        self.w_progress = w_progress
        self.low_energy_threshold = low_energy_threshold

    def get_neighbors(self, x, y, size):
        neighbors = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                neighbors.append((nx, ny))
        return neighbors

    def distance(self, a, b):
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def decide(
        self,
        position,
        science_map,
        hazard_map,
        resources,
        global_goal=None,
        previous_position=None,
        visited_positions=None
    ):
        x, y = position
        size = science_map.shape[0]

        if visited_positions is None:
            visited_positions = []

        # Guardrails
        if resources["comms_state"] == "LOST":
            return {
                "mode": "SAFE_STOP",
                "target": position,
                "reason": "Communications lost"
            }

        if resources["energy_state"] < self.low_energy_threshold:
            return {
                "mode": "RETURN",
                "target": (0, 0),
                "reason": "Low energy"
            }

        candidates = self.get_neighbors(x, y, size)

        best_score = -999
        best_target = position
        best_reason = "No better option"

        current_dist_to_goal = 0.0
        if global_goal is not None:
            current_dist_to_goal = self.distance(position, global_goal)

        for nx, ny in candidates:
            science_score = science_map[nx, ny]
            hazard_score = hazard_map[nx, ny]

            return_penalty = 0.0
            if previous_position is not None and (nx, ny) == previous_position:
                return_penalty = self.w_return_penalty

            visit_penalty = 0.0
            if (nx, ny) in visited_positions:
                visit_penalty = self.w_visit_penalty

            progress_reward = 0.0
            if global_goal is not None:
                new_dist_to_goal = self.distance((nx, ny), global_goal)
                progress_reward = current_dist_to_goal - new_dist_to_goal

            utility = (
                self.w_science * science_score
                - self.w_hazard * hazard_score
                - self.w_energy * (1.0 - resources["energy_state"])
                - return_penalty
                - visit_penalty
                + self.w_progress * progress_reward
            )

            if utility > best_score:
                best_score = utility
                best_target = (nx, ny)
                best_reason = (
                    f"science={science_score:.2f}, "
                    f"hazard={hazard_score:.2f}, "
                    f"progress={progress_reward:.2f}, "
                    f"return_penalty={return_penalty:.2f}, "
                    f"visit_penalty={visit_penalty:.2f}, "
                    f"utility={utility:.2f}"
                )

        return {
            "mode": "NORMAL",
            "target": best_target,
            "reason": best_reason
        }
