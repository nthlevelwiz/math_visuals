"""Animate a visual proof that sin(theta) = 1 / csc(theta).

The animation shows:
  * a point moving around the unit circle;
  * the right triangle whose vertical leg has length sin(theta);
  * a reciprocal triangle that completes a rectangle at x = csc(theta);
  * highlighted edges used to read sin(theta) and csc(theta);
  * scrolling plots of sin(theta), csc(theta), and 1 / csc(theta).

Run interactively:
    python sin_csc_visual_proof.py

Save a file instead:
    python sin_csc_visual_proof.py --save sin_csc_visual_proof.gif
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Polygon, Rectangle

EPSILON = 1.0e-3
DEFAULT_FRAMES = 240
DEFAULT_INTERVAL_MS = 45


def safe_csc(theta: float) -> float:
    """Return csc(theta), clipped away from sin(theta)=0 for drawing."""
    sin_theta = math.sin(theta)
    if abs(sin_theta) < EPSILON:
        sin_theta = EPSILON if sin_theta >= 0 else -EPSILON
    return 1.0 / sin_theta


def configure_axis(ax: plt.Axes) -> None:
    """Style the geometric construction axis."""
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.45, 4.25)
    ax.set_ylim(-0.35, 1.55)
    ax.axhline(0, color="0.35", linewidth=1)
    ax.axvline(0, color="0.35", linewidth=1)
    ax.grid(True, alpha=0.18)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Unit-circle geometry: sin(θ) is the reciprocal of csc(θ)")


def build_animation(frames: int = DEFAULT_FRAMES, interval: int = DEFAULT_INTERVAL_MS) -> animation.FuncAnimation:
    """Build and return the Matplotlib animation."""
    theta_values = np.linspace(0.18, math.pi - 0.18, frames)
    sin_values = np.sin(theta_values)
    csc_values = 1.0 / sin_values

    fig = plt.figure(figsize=(13, 7), constrained_layout=True)
    geometry_ax = fig.add_subplot(1, 2, 1)
    plot_ax = fig.add_subplot(1, 2, 2)
    configure_axis(geometry_ax)

    unit_circle = Circle((0, 0), 1, fill=False, color="black", linewidth=2)
    geometry_ax.add_patch(unit_circle)

    theta_arc = Arc((0, 0), 0.55, 0.55, theta1=0, theta2=10, color="#7b2cbf", linewidth=2)
    geometry_ax.add_patch(theta_arc)
    theta_label = geometry_ax.text(0.35, 0.08, "θ", color="#7b2cbf", fontsize=13, weight="bold")

    first_triangle = Polygon([[0, 0], [1, 0], [1, 0]], closed=True, facecolor="#4dabf7", alpha=0.22, edgecolor="#1c7ed6", linewidth=2)
    second_triangle = Polygon([[1, 0], [1, 1], [1, 1]], closed=True, facecolor="#ffd43b", alpha=0.25, edgecolor="#f08c00", linewidth=2)
    rectangle = Rectangle((0, 0), 1, 1, fill=False, linestyle="--", edgecolor="#868e96", linewidth=2, alpha=0.85)
    geometry_ax.add_patch(rectangle)
    geometry_ax.add_patch(first_triangle)
    geometry_ax.add_patch(second_triangle)

    radius_line = Line2D([], [], color="#1c7ed6", linewidth=3, label="unit radius")
    base_line = Line2D([], [], color="#495057", linewidth=2)
    sin_edge = Line2D([], [], color="#e03131", linewidth=5, solid_capstyle="round", label="sin(θ)")
    csc_edge = Line2D([], [], color="#2f9e44", linewidth=5, solid_capstyle="round", label="csc(θ)")
    reciprocal_edge = Line2D([], [], color="#e03131", linewidth=3, linestyle=":", label="1 / csc(θ)")
    for line in (radius_line, base_line, sin_edge, csc_edge, reciprocal_edge):
        geometry_ax.add_line(line)

    point, = geometry_ax.plot([], [], "o", color="#1864ab", markersize=9)
    top_point, = geometry_ax.plot([], [], "o", color="#2f9e44", markersize=7)

    formula_text = geometry_ax.text(
        0.02,
        1.45,
        "",
        fontsize=12,
        va="top",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.9, "edgecolor": "0.8"},
    )
    geometry_ax.legend(loc="lower right")

    plot_ax.set_title("Values over the moving angle")
    plot_ax.set_xlim(theta_values[0], theta_values[-1])
    plot_ax.set_ylim(0, 5.9)
    plot_ax.set_xlabel("θ (radians)")
    plot_ax.grid(True, alpha=0.25)
    sin_curve, = plot_ax.plot([], [], color="#e03131", linewidth=3, label="sin(θ)")
    reciprocal_curve, = plot_ax.plot([], [], color="#9c36b5", linewidth=2.5, linestyle="--", label="1 / csc(θ)")
    csc_curve, = plot_ax.plot([], [], color="#2f9e44", linewidth=3, label="csc(θ)")
    theta_marker = plot_ax.axvline(theta_values[0], color="black", linewidth=1.5, alpha=0.7)
    plot_ax.legend(loc="upper center")

    def update(frame: int):
        theta = float(theta_values[frame])
        x = math.cos(theta)
        y = math.sin(theta)
        csc = safe_csc(theta)
        reciprocal = 1.0 / csc
        csc_draw = min(csc, geometry_ax.get_xlim()[1] - 0.25)

        # Main unit-circle right triangle: (0,0) -> (x,0) -> (x,y).
        first_triangle.set_xy([[0, 0], [x, 0], [x, y]])
        radius_line.set_data([0, x], [0, y])
        base_line.set_data([0, x], [0, 0])
        sin_edge.set_data([x, x], [0, y])
        point.set_data([x], [y])

        # Rectangle with height sin(theta) and width csc(theta). Its area is 1.
        rectangle.set_bounds(0, 0, csc_draw, y)
        csc_edge.set_data([0, csc_draw], [y, y])
        reciprocal_edge.set_data([csc_draw, csc_draw], [0, y])
        top_point.set_data([csc_draw], [y])

        # Second triangle completes the rectangle and emphasizes the reciprocal construction.
        second_triangle.set_xy([[x, 0], [x, y], [csc_draw, y]])

        theta_arc.theta2 = math.degrees(theta)
        theta_label.set_position((0.36 * math.cos(theta / 2), 0.36 * math.sin(theta / 2)))

        formula_text.set_text(
            "Highlighted lengths:\n"
            f"sin(θ) = vertical red edge = {y:.3f}\n"
            f"csc(θ) = top green edge = {csc:.3f}\n"
            f"1 / csc(θ) = {reciprocal:.3f}\n\n"
            "Because csc(θ) is defined as 1/sin(θ),\n"
            "taking its reciprocal gives sin(θ)."
        )

        visible_theta = theta_values[: frame + 1]
        sin_curve.set_data(visible_theta, sin_values[: frame + 1])
        reciprocal_curve.set_data(visible_theta, 1.0 / csc_values[: frame + 1])
        csc_curve.set_data(visible_theta, np.minimum(csc_values[: frame + 1], plot_ax.get_ylim()[1]))
        theta_marker.set_xdata([theta, theta])

        return (
            first_triangle,
            second_triangle,
            rectangle,
            radius_line,
            base_line,
            sin_edge,
            csc_edge,
            reciprocal_edge,
            point,
            top_point,
            theta_arc,
            theta_label,
            formula_text,
            sin_curve,
            reciprocal_curve,
            csc_curve,
            theta_marker,
        )

    return animation.FuncAnimation(fig, update, frames=frames, interval=interval, blit=False, repeat=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", type=Path, help="Optional output path ending in .gif or a Matplotlib-supported movie extension.")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help="Number of animation frames.")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_MS, help="Delay between frames in milliseconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    anim = build_animation(frames=args.frames, interval=args.interval)
    if args.save:
        suffix = args.save.suffix.lower()
        if suffix == ".gif":
            anim.save(args.save, writer=animation.PillowWriter(fps=max(1, 1000 // args.interval)))
        else:
            anim.save(args.save, fps=max(1, 1000 // args.interval))
    else:
        plt.show()


if __name__ == "__main__":
    main()
