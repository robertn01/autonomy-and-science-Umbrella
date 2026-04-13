
import math


class ExecutionModel:
    def __init__(self, step_size_rover=1, step_size_drone=2):
        self.step_size_rover = step_size_rover
        self.step_size_drone = step_size_drone

    def _move_toward(self, current_pos, target_pos, step_size):
        x, y = current_pos
        tx, ty = target_pos

        dx = tx - x
        dy = ty - y

        if dx == 0 and dy == 0:
            return current_pos

        distance = math.sqrt(dx**2 + dy**2)
        if distance <= step_size:
            return target_pos

        nx = x + step_size * dx / distance
        ny = y + step_size * dy / distance

        return (round(nx), round(ny))

    def execute(self, rover_state, drone_state, decision_output):
        rover_pos = rover_state["position"]
        drone_pos = drone_state["position"]
        mode = decision_output["mode"]
        target = decision_output["target"]

        rover_action = "HOLD"
        drone_action = "IDLE"
        rover_next = rover_pos
        drone_next = drone_pos
        status = "WAITING"

        if mode == "NORMAL":
            rover_action = "MOVE_TO_TARGET"
            rover_next = self._move_toward(rover_pos, target, self.step_size_rover)
            drone_action = "FOLLOW_SUPPORT"
            drone_next = drone_pos
            status = "ROVER_TRAVERSE"

        elif mode == "SCOUT_READY":
            rover_action = "SLOW_ADVANCE"
            rover_next = self._move_toward(rover_pos, target, 1)
            drone_action = "SCOUT_AREA"
            drone_next = self._move_toward(drone_pos, target, self.step_size_drone)
            status = "DRONE_SCOUT"

        elif mode == "CAUTION":
            rover_action = "HOLD_POSITION"
            drone_action = "PREPARE_SCOUT"
            status = "CAUTION_MODE"

        elif mode == "SAFE":
            rover_action = "STOP"
            drone_action = "RETURN_TO_ROVER"
            drone_next = self._move_toward(drone_pos, rover_pos, self.step_size_drone)
            status = "SAFE_MODE"

        return {
            "rover_action": rover_action,
            "rover_next": rover_next,
            "drone_action": drone_action,
            "drone_next": drone_next,
            "status": status
        }
