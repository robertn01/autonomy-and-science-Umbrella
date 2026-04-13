import os
import matplotlib.pyplot as plt


def render_world(world, science_candidates, selected_target, execution_output, step):
    rover_pos = world["rover"]["position"]
    drone_pos = world["drone"]["position"]
    map_w, map_h = world["map_size"]
    hazards = world["hazards"]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, map_w)
    ax.set_ylim(0, map_h)
    ax.set_title(f"Mission Simulation - Step {step}")

    # draw hazards
    for (hx, hy), hval in hazards.items():
        size = 120 + 180 * hval
        alpha = 0.25 + 0.45 * hval
        ax.scatter(hx, hy, marker="s", s=size, c="red", alpha=alpha)
        ax.text(hx + 0.1, hy + 0.1, f"{hval:.1f}", fontsize=8, color="darkred")

    # science candidates
    for c in science_candidates:
        ax.scatter(c["x"], c["y"], marker="*", s=220, c="blue")
        ax.text(c["x"] + 0.2, c["y"] + 0.2, f"C{c['id']}", color="navy")

    # selected target
    ax.scatter(selected_target[0], selected_target[1], marker="o", s=260,
               facecolors="none", edgecolors="green", linewidths=2)

    # rover and drone
    ax.scatter(rover_pos[0], rover_pos[1], marker="s", s=180, c="black", label="Rover")
    ax.scatter(drone_pos[0], drone_pos[1], marker="^", s=180, c="orange", label="Drone")

    # planned next moves
    rn = execution_output["rover_next"]
    dn = execution_output["drone_next"]

    ax.plot([rover_pos[0], rn[0]], [rover_pos[1], rn[1]], linestyle="--", color="black")
    ax.plot([drone_pos[0], dn[0]], [drone_pos[1], dn[1]], linestyle=":", color="orange")

    text_block = (
        f"Rover action: {execution_output['rover_action']}\n"
        f"Drone action: {execution_output['drone_action']}\n"
        f"Status: {execution_output['status']}\n"
        f"Rover battery: {world['rover']['battery']:.2f}\n"
        f"Drone battery: {world['drone']['battery']:.2f}\n"
        f"Comms: {world['mission']['comms_quality']:.2f}\n"
        f"Wind: {world['mission']['wind_level']:.2f}\n"
        f"Hazard uncertainty: {world['mission']['hazard_uncertainty']:.2f}"
    )

    ax.text(
        0.02, 0.98, text_block,
        transform=ax.transAxes,
        va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.75)
    )

    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    os.makedirs("mission_sim/outputs", exist_ok=True)
    fig.savefig(f"mission_sim/outputs/step_{step:02d}.png", dpi=150, bbox_inches="tight")

    plt.show()
    plt.close(fig)
