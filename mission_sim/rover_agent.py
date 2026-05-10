from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any


@dataclass
class RoverAgent:
    name: str
    position: tuple[int, int]
    base_position: tuple[int, int]
    battery: float
    role: str
    sensor_range: int = 4
    step_size: int = 1
    battery_floor: float = 0.18
    path: list[list[int]] = field(default_factory=list)
    sampled_targets: set[int] = field(default_factory=set)
    peer_snapshot: dict[str, Any] = field(default_factory=dict)
    assigned_target: dict[str, Any] | None = None
    last_proposal: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.path.append([self.position[0], self.position[1]])

    def distance(self, a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def _hazard_penalty(self, target: dict[str, Any], hazards: dict[tuple[int, int], float]) -> float:
        tx = int(target["x"])
        ty = int(target["y"])
        penalty = hazards.get((tx, ty), 0.0) * 1.4
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                penalty += hazards.get((tx + dx, ty + dy), 0.0) * 0.08
        return penalty

    def score_target(self, target: dict[str, Any], hazards: dict[tuple[int, int], float]) -> float:
        target_pos = (int(target["x"]), int(target["y"]))
        science_score = float(target["science_score"]) * float(target["confidence"])
        distance_cost = self.distance(self.position, target_pos) * 0.10
        hazard_cost = self._hazard_penalty(target, hazards)
        novelty_bonus = 0.15 if int(target["id"]) not in self.sampled_targets else -1.0
        return science_score - distance_cost - hazard_cost + novelty_bonus

    def rank_targets(
        self,
        targets: list[dict[str, Any]],
        hazards: dict[tuple[int, int], float],
    ) -> list[tuple[float, dict[str, Any]]]:
        ranked: list[tuple[float, dict[str, Any]]] = []
        for target in targets:
            if target.get("sampled"):
                continue
            score = self.score_target(target, hazards)
            ranked.append((score, target))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked

    def select_target(
        self,
        targets: list[dict[str, Any]],
        hazards: dict[tuple[int, int], float],
    ) -> dict[str, Any] | None:
        ranked = self.rank_targets(targets, hazards)
        if not ranked:
            self.assigned_target = None
            self.last_proposal = {"target_id": None, "utility": -999.0}
            return None

        proposal_score, proposal_target = ranked[0]
        peer_target_id = self.peer_snapshot.get("proposal", {}).get("target_id")
        peer_utility = float(self.peer_snapshot.get("proposal", {}).get("utility", -999.0))

        if peer_target_id == proposal_target["id"] and peer_utility >= proposal_score:
            for score, target in ranked[1:]:
                if target["id"] != peer_target_id:
                    proposal_score = score
                    proposal_target = target
                    break

        self.assigned_target = proposal_target
        self.last_proposal = {
            "target_id": int(proposal_target["id"]),
            "utility": round(float(proposal_score), 3),
        }
        return proposal_target

    def _step_toward(self, target_position: tuple[int, int], map_size: tuple[int, int]) -> tuple[int, int]:
        if target_position == self.position:
            return self.position

        x, y = self.position
        tx, ty = target_position
        dx = tx - x
        dy = ty - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return self.position

        step_x = int(round(x + self.step_size * dx / distance))
        step_y = int(round(y + self.step_size * dy / distance))
        max_x, max_y = map_size
        step_x = max(0, min(max_x - 1, step_x))
        step_y = max(0, min(max_y - 1, step_y))
        return (step_x, step_y)

    def move(self, map_size: tuple[int, int]) -> tuple[str, tuple[int, int]]:
        if self.battery <= self.battery_floor:
            self.assigned_target = {"id": -1, "x": self.base_position[0], "y": self.base_position[1]}
            self.position = self._step_toward(self.base_position, map_size)
            self.battery = max(0.0, self.battery - 0.005)
            self.path.append([self.position[0], self.position[1]])
            return "RETURN_TO_BASE", self.position

        if self.assigned_target is None:
            self.battery = max(0.0, self.battery - 0.003)
            self.path.append([self.position[0], self.position[1]])
            return "HOLD", self.position

        target_position = (int(self.assigned_target["x"]), int(self.assigned_target["y"]))
        new_position = self._step_toward(target_position, map_size)
        self.position = new_position
        self.battery = max(0.0, self.battery - 0.008)
        self.path.append([self.position[0], self.position[1]])

        if self.position == target_position:
            self.sampled_targets.add(int(self.assigned_target["id"]))
            self.battery = max(0.0, self.battery - 0.015)
            return "SAMPLE", self.position

        return "TRAVERSE", self.position

    def update_peer_snapshot(self, message: dict[str, Any] | None) -> None:
        if message:
            self.peer_snapshot = message

    def telemetry(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "position": [self.position[0], self.position[1]],
            "battery": round(self.battery, 3),
            "health": "OK" if self.battery > 0.15 else "LOW_POWER",
            "role": self.role,
            "assigned_target_id": None if self.assigned_target is None else int(self.assigned_target["id"]),
            "proposal": self.last_proposal,
            "peer_snapshot": self.peer_snapshot,
            "path": self.path,
        }
