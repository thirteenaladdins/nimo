import vpype
from typing import List, Dict, Any
import logging
import os
import subprocess
import tempfile
import requests

logger = logging.getLogger(__name__)


def run(cmd):
    """Run a shell command and raise an exception if it fails"""
    subprocess.run(cmd, check=True)


def raster_to_svg(image_url: str, width_mm=160, height_mm=160, margin_mm=5,
                  simplify_mm=0.2, mode="outline") -> str:
    """Convert a raster image to an optimized SVG for plotting"""
    with tempfile.TemporaryDirectory() as td:
        ipath = os.path.join(td, "input.png")
        open(ipath, "wb").write(requests.get(image_url, timeout=30).content)

        # 1) preprocess → PBM
        prepped = os.path.join(td, "prepped.pbm")
        run(["magick", ipath,
             "-resize", "1600x1600>",
             "-colorspace", "Gray",
             "-contrast-stretch", "1%x1%",
             "-despeckle",
             "-auto-threshold", "OTSU",
             prepped])

        # 2) vectorize → raw.svg
        raw_svg = os.path.join(td, "raw.svg")
        if mode == "centerline":
            # autotrace centerline (installed via apt)
            run(["autotrace", "--centerline", "--filter-iterations", "3",
                 "--output-file", raw_svg, prepped])
        else:
            # outline with potrace
            run(["potrace", prepped, "--svg", "-o", raw_svg])

        # 3) optimize & layout → plot.svg
        plot_svg = os.path.join(td, "plot.svg")
        run([
            "vpype", "read", raw_svg,
            "linemerge",
            "linesimplify", f"{simplify_mm}mm",
            "linesort", "reloop",
            "layout", f"{width_mm}x{height_mm}mm",
            "--center", "--fit-to-margins", f"{margin_mm}mm",
            "write", plot_svg
        ])

        return open(plot_svg, "r", encoding="utf-8").read()


class PlotterPipeline:
    """Handles plotter operations and pipeline processing"""

    def __init__(self):
        self.document = vpype.Document()

    def load_svg(self, svg_path: str) -> bool:
        """Load an SVG file into the pipeline"""
        try:
            self.document = vpype.read_svg(svg_path)
            logger.info(f"Successfully loaded SVG: {svg_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load SVG {svg_path}: {e}")
            return False

    def load_svg_content(self, svg_content: str) -> bool:
        """Load SVG content directly into the pipeline"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as tmp:
                tmp.write(svg_content)
                tmp_path = tmp.name

            success = self.load_svg(tmp_path)
            os.unlink(tmp_path)  # Clean up temp file
            return success
        except Exception as e:
            logger.error(f"Failed to load SVG content: {e}")
            return False

    def optimize_paths(self) -> bool:
        """Optimize the paths for plotting"""
        try:
            # Apply vpype operations for optimization
            self.document = vpype.merge(self.document)
            self.document = vpype.linemerge(self.document)
            logger.info("Paths optimized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to optimize paths: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current document"""
        try:
            stats = {
                "layer_count": len(self.document.layers),
                "total_paths": sum(len(layer) for layer in self.document.layers.values()),
                "bounds": self.document.bounds if self.document.bounds else None
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def export_gcode(self, output_path: str) -> bool:
        """Export the document as G-code"""
        try:
            # This would need to be implemented based on your specific plotter
            # For now, we'll just log the intention
            logger.info(f"Would export G-code to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export G-code: {e}")
            return False
