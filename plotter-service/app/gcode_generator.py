"""
G-code Generator Module

Converts SVG paths to optimized G-code for plotters.
Handles path optimization, pen up/down commands, and efficient movement.
"""

import re
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GCodeSettings:
    """Settings for G-code generation"""
    feed_rate: float = 1000.0  # mm/min
    pen_up_height: float = 5.0  # mm above surface
    pen_down_height: float = 0.0  # mm at surface
    safe_height: float = 10.0  # mm for rapid moves
    units: str = "mm"  # mm or inches


class SVGToGCode:
    """Convert SVG paths to optimized G-code"""

    def __init__(self, settings: Optional[GCodeSettings] = None):
        self.settings = settings or GCodeSettings()
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = self.settings.safe_height

    def parse_svg_path(self, svg_content: str) -> List[Tuple[float, float]]:
        """Extract coordinates from SVG path"""
        # Find the path element
        path_match = re.search(r'<path[^>]*d="([^"]*)"', svg_content)
        if not path_match:
            return []

        path_data = path_match.group(1)
        coordinates = []

        # Parse path commands (M, L, etc.)
        commands = re.findall(r'([ML])\s*([^ML]+)', path_data)

        for cmd, coords in commands:
            if cmd == 'M':  # Move to (absolute)
                x, y = map(float, coords.strip().split())
                coordinates.append((x, y))
            elif cmd == 'L':  # Line to (absolute)
                x, y = map(float, coords.strip().split())
                coordinates.append((x, y))

        return coordinates

    def optimize_paths(self, coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Optimize path order to minimize travel distance"""
        if len(coordinates) <= 2:
            return coordinates

        # Simple nearest neighbor optimization
        optimized = [coordinates[0]]
        remaining = set(coordinates[1:])

        while remaining:
            current = optimized[-1]
            nearest = min(remaining, key=lambda p: self.distance(current, p))
            optimized.append(nearest)
            remaining.remove(nearest)

        return optimized

    def distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def generate_gcode(self, svg_content: str) -> str:
        """Generate G-code from SVG content"""
        coordinates = self.parse_svg_path(svg_content)
        if not coordinates:
            return ""

        # Optimize path order
        optimized_coords = self.optimize_paths(coordinates)

        gcode_lines = []

        # Header
        gcode_lines.extend([
            f"; G-code generated from SVG",
            f"; Units: {self.settings.units}",
            f"; Feed rate: {self.settings.feed_rate} {self.settings.units}/min",
            f"G21 ; Set units to mm",
            f"G90 ; Absolute positioning",
            f"G0 Z{self.settings.safe_height} ; Move to safe height",
            f"G0 X0 Y0 ; Move to origin",
            ""
        ])

        # Process each coordinate
        for i, (x, y) in enumerate(optimized_coords):
            if i == 0:
                # First point - move to position
                gcode_lines.append(f"G0 X{x:.3f} Y{y:.3f} ; Move to start")
                gcode_lines.append(
                    f"G0 Z{self.settings.pen_down_height} ; Lower pen")
            else:
                # Subsequent points - draw line
                gcode_lines.append(
                    f"G1 X{x:.3f} Y{y:.3f} F{self.settings.feed_rate} ; Draw line")

        # Footer
        gcode_lines.extend([
            f"G0 Z{self.settings.safe_height} ; Raise pen",
            f"G0 X0 Y0 ; Return to origin",
            f"M2 ; End program"
        ])

        return "\n".join(gcode_lines)


def svg_to_gcode(svg_content: str, settings: Optional[GCodeSettings] = None) -> str:
    """Convenience function to convert SVG to G-code"""
    converter = SVGToGCode(settings)
    return converter.generate_gcode(svg_content)
