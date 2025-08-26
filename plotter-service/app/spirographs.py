"""
Spirograph Generator Module

Generates hypotrochoid and epitrochoid patterns for plotter art.
Clean, reusable functions that can be integrated into the daily art system.
"""

import math
import random
from typing import List, Tuple, Optional
import numpy as np


def hypotrochoid(R: float, r: float, d: float, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate hypotrochoid coordinates.

    Args:
        R: Fixed circle radius
        r: Rolling circle radius (inside)
        d: Pen offset distance
        t: Angle array in radians

    Returns:
        Tuple of (x, y) coordinate arrays
    """
    x = (R - r) * np.cos(t) + d * np.cos(((R - r) / r) * t)
    y = (R - r) * np.sin(t) - d * np.sin(((R - r) / r) * t)
    return x, y


def epitrochoid(R: float, r: float, d: float, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate epitrochoid coordinates.

    Args:
        R: Fixed circle radius
        r: Rolling circle radius (outside)
        d: Pen offset distance
        t: Angle array in radians

    Returns:
        Tuple of (x, y) coordinate arrays
    """
    x = (R + r) * np.cos(t) - d * np.cos(((R + r) / r) * t)
    y = (R + r) * np.sin(t) - d * np.sin(((R + r) / r) * t)
    return x, y


def lcm(a: int, b: int) -> int:
    """Calculate least common multiple of two integers."""
    from math import gcd
    return abs(a * b) // gcd(a, b)


def closed_theta(R: float, r: float, epi: bool = False) -> float:
    """
    Calculate the angle needed for a closed curve.

    Args:
        R: Fixed circle radius
        r: Rolling circle radius
        epi: True for epitrochoid, False for hypotrochoid

    Returns:
        Angle in radians for complete curve
    """
    R_i, r_i = int(round(R)), int(round(r))
    if epi:
        k = lcm(R_i + r_i, r_i) / r_i
    else:
        k = lcm(abs(R_i - r_i), r_i) / r_i
    return 2 * math.pi * k


def coordinates_to_svg_path(xs: np.ndarray, ys: np.ndarray) -> str:
    """
    Convert coordinate arrays to SVG path string.

    Args:
        xs: X coordinates array
        ys: Y coordinates array

    Returns:
        SVG path string
    """
    if len(xs) == 0:
        return ""

    path_cmds = [f"M {xs[0]:.3f} {ys[0]:.3f}"]
    for x, y in zip(xs[1:], ys[1:]):
        path_cmds.append(f"L {x:.3f} {y:.3f}")
    return " ".join(path_cmds)


def generate_spirograph_svg(
    width_mm: float = 160.0,
    height_mm: float = 160.0,
    margin_mm: float = 5.0,
    stroke_width: float = 0.2,
    seed: Optional[int] = None
) -> str:
    """
    Generate a random spirograph SVG.

    Args:
        width_mm: SVG width in mm
        height_mm: SVG height in mm
        margin_mm: Margin around drawing area
        stroke_width: Stroke width in mm
        seed: Random seed for reproducible results

    Returns:
        SVG string
    """
    if seed is not None:
        random.seed(seed)

    # Drawing area
    draw_w = width_mm - 2 * margin_mm
    draw_h = height_mm - 2 * margin_mm
    scale = min(draw_w, draw_h) / 2.0

    # Predefined parameter sets for good-looking patterns
    param_sets = [
        (60, 13, 18, "hypo"),
        (55, 21, 11, "hypo"),
        (50, 23, 40, "epi"),
        (48, 17, 25, "hypo"),
        (52, 7, 30, "hypo"),
        (58, 31, 16, "epi"),
        (62, 14, 29, "epi"),
        (56, 19, 12, "hypo"),
        (45, 15, 22, "hypo"),
        (65, 28, 19, "epi"),
        (42, 11, 35, "hypo"),
        (68, 33, 14, "epi"),
    ]

    # Pick a random parameter set
    R, r, d, kind = random.choice(param_sets)

    # Calculate closed curve parameters
    T = closed_theta(R, r, epi=(kind == "epi"))
    samples = 4000  # Dense enough for smooth lines
    t = np.linspace(0, T, samples, endpoint=True)

    # Generate coordinates
    if kind == "hypo":
        x, y = hypotrochoid(R, r, d, t)
    else:
        x, y = epitrochoid(R, r, d, t)

    # Normalize to fit drawing area
    max_extent = max(np.max(np.abs(x)), np.max(np.abs(y)))
    s = scale / max_extent
    xs = x * s
    ys = y * s

    # Create SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" 
    width="{width_mm}mm" height="{height_mm}mm" 
    viewBox="0 0 {width_mm} {height_mm}">
    <g transform="translate({width_mm/2},{height_mm/2})">
        <path d="{coordinates_to_svg_path(xs, ys)}" 
              fill="none" stroke="black" 
              stroke-width="{stroke_width}"/>
    </g>
</svg>'''

    return svg


def generate_spirograph_pack(
    count: int = 8,
    width_mm: float = 80.0,
    height_mm: float = 80.0,
    margin_mm: float = 5.0,
    stroke_width: float = 0.2,
    seed: Optional[int] = None
) -> List[str]:
    """
    Generate multiple spirograph SVGs.

    Args:
        count: Number of SVGs to generate
        width_mm: SVG width in mm
        height_mm: SVG height in mm
        margin_mm: Margin around drawing area
        stroke_width: Stroke width in mm
        seed: Random seed for reproducible results

    Returns:
        List of SVG strings
    """
    if seed is not None:
        random.seed(seed)

    svgs = []
    for i in range(count):
        svg = generate_spirograph_svg(
            width_mm=width_mm,
            height_mm=height_mm,
            margin_mm=margin_mm,
            stroke_width=stroke_width,
            seed=seed + i if seed is not None else None
        )
        svgs.append(svg)

    return svgs


# Convenience function for daily art
def get_daily_spirograph(seed: Optional[int] = None) -> str:
    """
    Get a spirograph for daily art (160x160mm).

    Args:
        seed: Random seed (typically date-based)

    Returns:
        SVG string for daily art
    """
    return generate_spirograph_svg(
        width_mm=160.0,
        height_mm=160.0,
        margin_mm=5.0,
        stroke_width=0.2,
        seed=seed
    )
