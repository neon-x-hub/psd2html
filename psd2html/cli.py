"""Command-line interface for PSD2HTML."""

import argparse
import sys
from pathlib import Path
from . import __version__
from .core.psd_parser import PSDParser
from .core.layout_resolver import LayoutResolver
from .exporters.json_exporter import JSONExporter
from .exporters.html_generator import HTMLCSSGenerator


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="psd2html",
        description="Convert Photoshop (.psd) layouts into structured JSON and HTML/CSS.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "psd_path",
        type=str,
        help="Path to the source Photoshop (.psd) file.",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="output_dir",
        type=str,
        default="dist",
        help="Directory to save generated files (default: dist).",
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest="canvas_mode",
        choices=["viewport", "fixed"],
        default="viewport",
        help="Artboard/canvas sizing mode: 'viewport' (default: responsive to viewport size) or 'fixed' (exact PSD pixel bounds).",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["all", "html", "json"],
        default="all",
        help="Output format to generate (default: all).",
    )
    parser.add_argument(
        "--no-vector-geom",
        dest="use_vector_geometry",
        action="store_false",
        help="Use raster channel bounding boxes instead of vector origination rectangles.",
    )
    parser.add_argument(
        "--no-clamp",
        dest="clamp_negative_coords",
        action="store_false",
        help="Do not clamp negative coordinates to zero.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )

    parsed = parser.parse_args(args)
    psd_file = Path(parsed.psd_path)

    if not psd_file.exists():
        print(f"Error: PSD file not found at '{psd_file}'", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(parsed.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Processing PSD layout: {psd_file.name}")

    # 1. Parse PSD
    psd_parser = PSDParser(
        include_hidden=True,
        use_vector_geometry=parsed.use_vector_geometry,
    )
    canvas_bbox, raw_root = psd_parser.parse_file(psd_file)
    if parsed.verbose:
        print(f"    Canvas dimensions: {int(canvas_bbox.width)}x{int(canvas_bbox.height)} px")
        print(f"    Root layer: {raw_root.name} ({raw_root.kind})")

    # 2. Resolve Layout
    resolver = LayoutResolver(
        canvas_mode=parsed.canvas_mode,
        clamp_negative_coords=parsed.clamp_negative_coords,
    )
    document = resolver.resolve(canvas_bbox, raw_root)
    if parsed.verbose:
        print(f"    Total top-level elements: {len(document.root_node.children)}")

    # 3. Export
    generated_files = []

    if parsed.output_format in ("all", "json"):
        json_exporter = JSONExporter(indent=2)
        json_path = out_dir / f"{psd_file.stem}.layout.json"
        json_exporter.export_file(document, json_path)
        generated_files.append(json_path)

    if parsed.output_format in ("all", "html"):
        html_gen = HTMLCSSGenerator(include_comments=True)
        html_path, css_path = html_gen.export_files(document, out_dir, standalone=True)
        generated_files.extend([html_path, css_path])

    print("[+] Conversion completed successfully:")
    for f in generated_files:
        print(f"    -> {f}")


if __name__ == "__main__":
    main()
