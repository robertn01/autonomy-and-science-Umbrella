class CandidateDecisionManager:
    def __init__(
        self,
        w_science=1.0,
        w_confidence=0.5,
        w_hazard=1.2,
        w_energy=0.8,
        w_distance=0.7,
        low_energy_threshold=0.2
    ):
        self.w_science = w_science
        self.w_confidence = w_confidence
        self.w_hazard = w_hazard
        self.w_energy = w_energy
        self.w_distance = w_distance
        self.low_energy_threshold = low_energy_threshold

    def decide(self, science_candidates, resource_state, hazard_overrides, rover_position):
        # Guardrails
        if resource_state["comms_state"] == "LOST":
            return {
                "selected_target_id": None,
                "selected_target_xy": rover_position,
                "mode": "SAFE_STOP",
                "action": "STOP",
                "reason": "Communications lost"
            }

        if resource_state["energy_state"] < self.low_energy_threshold:
            return {
                "selected_target_id": None,
                "selected_target_xy": (0, 0),
                "mode": "RETURN",
                "action": "RETURN_TO_BASE",
                "reason": "Low energy"
            }

        best_score = -999
        best_candidate = None
        best_reason = "No candidate selected"

        for candidate in science_candidates:
            cid = candidate["id"]
            science_score = candidate["science_score"]
            confidence = candidate["confidence"]

            hazard_score = hazard_overrides[cid]["hazard_score"]
            distance_cost = hazard_overrides[cid]["distance_cost"]

            utility = (
                self.w_science * science_score
                + self.w_confidence * confidence
                - self.w_hazard * hazard_score
                - self.w_energy * (1.0 - resource_state["energy_state"])
                - self.w_distance * distance_cost
            )

            if utility > best_score:
                best_score = utility
                best_candidate = candidate
                best_reason = (
                    f"id={cid}, mineral={candidate['mineral_type']}, "
                    f"science={science_score:.2f}, confidence={confidence:.2f}, "
                    f"hazard={hazard_score:.2f}, distance={distance_cost:.2f}, "
                    f"utility={utility:.2f}"
                )

        return {
            "selected_target_id": best_candidate["id"],
            "selected_target_xy": (best_candidate["x"], best_candidate["y"]),
            "mode": "NORMAL",
            "action": "GO_TO_TARGET",
            "reason": best_reason
        }
