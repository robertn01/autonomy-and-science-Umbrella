from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Any

from mission_sim.rover_agent import RoverAgent


@dataclass
class Message:
    deliver_step: int
    sender: str
    recipient: str
    payload: dict[str, Any]


class SwarmLink:
    def __init__(self, latency_range: tuple[int, int] = (1, 3), loss_probability: float = 0.12) -> None:
        self.latency_range = latency_range
        self.loss_probability = loss_probability
        self._queue: deque[Message] = deque()
        self.delivered_count = 0
        self.dropped_count = 0

    def publish(self, current_step: int, sender: str, recipient: str, payload: dict[str, Any]) -> None:
        if random.random() < self.loss_probability:
            self.dropped_count += 1
            return
        delay = random.randint(self.latency_range[0], self.latency_range[1])
        self._queue.append(
            Message(
                deliver_step=current_step + delay,
                sender=sender,
                recipient=recipient,
                payload=payload,
            )
        )

    def collect(self, current_step: int, recipient: str) -> list[dict[str, Any]]:
        ready: list[dict[str, Any]] = []
        remaining: deque[Message] = deque()
        while self._queue:
            message = self._queue.popleft()
            if message.deliver_step <= current_step and message.recipient == recipient:
                self.delivered_count += 1
                ready.append({"sender": message.sender, **message.payload})
            else:
                remaining.append(message)
        self._queue = remaining
        return ready

    def pending_count(self) -> int:
        return len(self._queue)


class MarsSwarmSimulator:
    def __init__(self, seed: int = 17) -> None:
        self.seed = seed
        self.random = random.Random(seed)
        self.map_size = (24, 24)
        self.hazards = self._generate_hazards()
        self.targets = self._generate_targets()
        self.link = SwarmLink()
        self.rovers = [
            RoverAgent("Rover A", (2, 3), (1, 1), 0.82, "science_scout"),
            RoverAgent("Rover B", (20, 20), (22, 22), 0.76, "terrain_mapper"),
        ]
        self.step_index = 0
        self.sampled_targets: set[int] = set()
        self.event_log: list[dict[str, Any]] = []

    def _generate_hazards(self) -> dict[tuple[int, int], float]:
        hazards: dict[tuple[int, int], float] = {}
        for _ in range(22):
            x = self.random.randint(1, self.map_size[0] - 2)
            y = self.random.randint(1, self.map_size[1] - 2)
            hazards[(x, y)] = round(self.random.uniform(0.25, 0.95), 2)
        return hazards

    def _generate_targets(self) -> list[dict[str, Any]]:
        candidates = [
            (4, 17, 0.93, 0.78, "clay-rich ridge"),
            (8, 7, 0.81, 0.91, "layered basalt"),
            (14, 13, 0.74, 0.87, "sulfate outcrop"),
            (18, 5, 0.69, 0.82, "sediment fan"),
            (12, 19, 0.88, 0.80, "hydrated deposit"),
        ]
        targets: list[dict[str, Any]] = []
        for idx, (x, y, science_score, confidence, terrain) in enumerate(candidates, start=1):
            targets.append(
                {
                    "id": idx,
                    "x": x,
                    "y": y,
                    "science_score": science_score,
                    "confidence": confidence,
                    "terrain": terrain,
                    "sampled": False,
                    "claimed_by": None,
                }
            )
        return targets

    def _target_by_id(self, target_id: int | None) -> dict[str, Any] | None:
        if target_id is None:
            return None
        for target in self.targets:
            if int(target["id"]) == int(target_id):
                return target
        return None

    def _clear_claims(self) -> None:
        for target in self.targets:
            if not target["sampled"]:
                target["claimed_by"] = None

    def _apply_peer_views(self) -> None:
        for rover in self.rovers:
            peer_name = self.rovers[1].name if rover.name == self.rovers[0].name else self.rovers[0].name
            messages = self.link.collect(self.step_index, rover.name)
            peer_snapshot = rover.peer_snapshot.copy()
            for message in messages:
                if message["sender"] == peer_name:
                    peer_snapshot = message
            rover.update_peer_snapshot(peer_snapshot)

    def _build_message(self, rover: RoverAgent) -> dict[str, Any]:
        return {
            "step": self.step_index,
            "telemetry": rover.telemetry(),
            "proposal": rover.last_proposal,
        }

    def _assign_targets(self) -> None:
        for target in self.targets:
            target["claimed_by"] = None

        proposals: dict[str, dict[str, Any] | None] = {}
        ranked: dict[str, list[tuple[float, dict[str, Any]]]] = {}
        for rover in self.rovers:
            ranked[rover.name] = rover.rank_targets(self.targets, self.hazards)
            rover.select_target(self.targets, self.hazards)
            proposals[rover.name] = rover.assigned_target

        rover_a, rover_b = self.rovers
        proposal_a = proposals[rover_a.name]
        proposal_b = proposals[rover_b.name]

        if proposal_a is None and proposal_b is None:
            return

        if proposal_a is not None and proposal_b is not None and proposal_a["id"] == proposal_b["id"]:
            score_a = ranked[rover_a.name][0][0] if ranked[rover_a.name] else -999.0
            score_b = ranked[rover_b.name][0][0] if ranked[rover_b.name] else -999.0
            if score_a >= score_b:
                proposals[rover_b.name] = self._next_best_target(rover_b, proposal_a["id"], ranked)
            else:
                proposals[rover_a.name] = self._next_best_target(rover_a, proposal_b["id"], ranked)

        for rover in self.rovers:
            rover.assigned_target = proposals[rover.name]
            if rover.assigned_target is not None:
                target = self._target_by_id(rover.assigned_target["id"])
                if target is not None and not target["sampled"]:
                    target["claimed_by"] = rover.name

    def _next_best_target(
        self,
        rover: RoverAgent,
        excluded_target_id: int,
        ranked: dict[str, list[tuple[float, dict[str, Any]]]],
    ) -> dict[str, Any] | None:
        for _, target in ranked[rover.name][1:]:
            if int(target["id"]) != int(excluded_target_id) and not target["sampled"]:
                return target
        return None

    def _consensus_target(self) -> dict[str, Any] | None:
        best: tuple[float, dict[str, Any]] | None = None
        for target in self.targets:
            if target["sampled"]:
                continue
            local_scores = [rover.score_target(target, self.hazards) for rover in self.rovers]
            consensus_score = sum(local_scores) / len(local_scores)
            if best is None or consensus_score > best[0]:
                best = (consensus_score, target)
        if best is None:
            return None
        target = best[1]
        return {
            "id": int(target["id"]),
            "x": int(target["x"]),
            "y": int(target["y"]),
            "science_score": target["science_score"],
            "confidence": target["confidence"],
            "terrain": target["terrain"],
            "utility": round(best[0], 3),
        }

    def step(self) -> dict[str, Any]:
        self._apply_peer_views()
        self._assign_targets()

        step_events: list[dict[str, Any]] = []
        for rover in self.rovers:
            action, _ = rover.move(self.map_size)
            if action == "SAMPLE" and rover.assigned_target is not None:
                target = self._target_by_id(rover.assigned_target["id"])
                if target is not None:
                    target["sampled"] = True
                    target["claimed_by"] = rover.name
                    self.sampled_targets.add(int(target["id"]))
                    step_events.append(
                        {
                            "type": "sample",
                            "rover": rover.name,
                            "target_id": int(target["id"]),
                            "terrain": target["terrain"],
                        }
                    )

        self._clear_claims()

        for rover in self.rovers:
            peer_name = self.rovers[1].name if rover.name == self.rovers[0].name else self.rovers[0].name
            self.link.publish(
                self.step_index,
                rover.name,
                peer_name,
                self._build_message(rover),
            )

        if step_events:
            self.event_log.extend(step_events)

        mission_comms = max(0.35, 0.95 - 0.02 * self.link.pending_count())
        explored_ratio = round(len(self.sampled_targets) / len(self.targets), 3)
        self.step_index += 1

        return {
            "step": self.step_index,
            "map_size": [self.map_size[0], self.map_size[1]],
            "hazards": [
                {"x": x, "y": y, "intensity": intensity}
                for (x, y), intensity in sorted(self.hazards.items())
            ],
            "science_targets": self.targets,
            "rovers": [rover.telemetry() for rover in self.rovers],
            "consensus_target": self._consensus_target(),
            "network": {
                "queued": self.link.pending_count(),
                "delivered": self.link.delivered_count,
                "dropped": self.link.dropped_count,
                "comms_quality": round(mission_comms, 3),
            },
            "mission": {
                "explored_ratio": explored_ratio,
                "sampled_targets": len(self.sampled_targets),
                "step_index": self.step_index,
            },
            "events": self.event_log[-6:],
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "step": self.step_index,
            "map_size": [self.map_size[0], self.map_size[1]],
            "hazards": [
                {"x": x, "y": y, "intensity": intensity}
                for (x, y), intensity in sorted(self.hazards.items())
            ],
            "science_targets": self.targets,
            "rovers": [rover.telemetry() for rover in self.rovers],
            "consensus_target": self._consensus_target(),
            "network": {
                "queued": self.link.pending_count(),
                "delivered": self.link.delivered_count,
                "dropped": self.link.dropped_count,
                "comms_quality": 0.95,
            },
            "mission": {
                "explored_ratio": round(len(self.sampled_targets) / len(self.targets), 3),
                "sampled_targets": len(self.sampled_targets),
                "step_index": self.step_index,
            },
            "events": self.event_log[-6:],
        }
