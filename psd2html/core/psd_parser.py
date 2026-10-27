"""PSD parser module using psd-tools."""

from pathlib import Path
from typing import Optional, List, Tuple
from psd_tools import PSDImage
from psd_tools.constants import Tag

from .models import BoundingBox, RawLayer
from .metadata_parser import MetadataParser


class PSDParser:
    """Extracts raw hierarchy, geometry, and styling from a PSD file."""

    def __init__(self, include_hidden: bool = True, use_vector_geometry: bool = True):
        self.include_hidden = include_hidden
        self.use_vector_geometry = use_vector_geometry

    def parse_file(self, file_path: str | Path) -> Tuple[BoundingBox, RawLayer]:
        """Parse a PSD file into a canvas bounding box and a root RawLayer."""
        psd = PSDImage.open(file_path)
        canvas_width = psd.width
        canvas_height = psd.height
        canvas_bbox = BoundingBox(0.0, 0.0, float(canvas_width), float(canvas_height))

        # Check if the document has a single top-level Artboard
        root_children: List[RawLayer] = []
        for top_layer in psd:
            if not self.include_hidden and not top_layer.is_visible():
                continue
            child_raw = self._parse_layer(top_layer)
            if child_raw:
                root_children.append(child_raw)

        # If there's an artboard at root, adjust canvas bounds
        if len(root_children) == 1 and root_children[0].kind == "artboard":
            artboard = root_children[0]
            canvas_bbox = artboard.bbox
            root_layer = artboard
        else:
            root_metadata = MetadataParser.parse("Root | w-rel h-rel left-abs top-abs")
            root_layer = RawLayer(
                name="Root",
                kind="canvas",
                bbox=canvas_bbox,
                visible=True,
                opacity=1.0,
                metadata=root_metadata,
                children=root_children,
            )

        return canvas_bbox, root_layer

    def _parse_layer(self, layer) -> Optional[RawLayer]:
        """Recursively extracts a RawLayer from a psd-tools layer."""
        if not self.include_hidden and not layer.is_visible():
            return None

        name = layer.name or ""
        kind = getattr(layer, "kind", "layer")
        visible = layer.is_visible()
        opacity = float(layer.opacity) / 255.0 if hasattr(layer, "opacity") else 1.0

        # Extract geometry
        bbox = self._extract_bbox(layer)

        # Extract vector styling (fill, stroke)
        fill_color = self._extract_fill_color(layer)
        stroke_color, stroke_width = self._extract_stroke(layer)

        # Parse layer metadata notation
        metadata = MetadataParser.parse(name)

        # Process children if layer is a group or artboard
        children: List[RawLayer] = []
        if layer.is_group():
            for child in layer:
                child_layer = self._parse_layer(child)
                if child_layer:
                    children.append(child_layer)

        # Skip zero-sized empty layers with no children (e.g. initial empty raster layers)
        if bbox.width == 0 and bbox.height == 0 and not children:
            return None

        return RawLayer(
            name=name,
            kind=kind,
            bbox=bbox,
            visible=visible,
            opacity=opacity,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            metadata=metadata,
            children=children,
        )

    def _extract_bbox(self, layer) -> BoundingBox:
        """Extract pixel bounds, favoring vector origination when available."""
        if self.use_vector_geometry and hasattr(layer, "origination") and layer.origination:
            try:
                orig = layer.origination[0]
                if hasattr(orig, "bbox") and orig.bbox:
                    l, t, r, b = orig.bbox
                    return BoundingBox(float(l), float(t), float(r), float(b))
            except Exception:
                pass

        if hasattr(layer, "bbox") and layer.bbox:
            l, t, r, b = layer.bbox
            return BoundingBox(float(l), float(t), float(r), float(b))

        return BoundingBox(0.0, 0.0, 0.0, 0.0)

    def _extract_fill_color(self, layer) -> Optional[str]:
        """Extract solid fill color as hex string."""
        if not hasattr(layer, "tagged_blocks") or not layer.tagged_blocks:
            return None

        # Check Tag.VECTOR_STROKE_CONTENT_DATA
        block = layer.tagged_blocks.get(Tag.VECTOR_STROKE_CONTENT_DATA)
        if block:
            data = getattr(block, "data", block)
            clr = self._find_color_in_dict(data)
            if clr:
                return clr

        # Check solid color adjustment layer block
        soco = layer.tagged_blocks.get(b"SoCo")
        if soco:
            data = getattr(soco, "data", soco)
            clr = self._find_color_in_dict(data)
            if clr:
                return clr

        return None

    def _find_color_in_dict(self, data) -> Optional[str]:
        """Helper to find RGB color from PSD descriptor dictionary."""
        if not hasattr(data, "get"):
            return None
        clr = data.get(b"Clr ") or data.get("Clr ")
        if clr and hasattr(clr, "get"):
            r = float(clr.get(b"Rd  ") or clr.get("Rd  ") or 0.0)
            g = float(clr.get(b"Grn ") or clr.get("Grn ") or 0.0)
            b = float(clr.get(b"Bl  ") or clr.get("Bl  ") or 0.0)
            return f"#{int(round(r)):02x}{int(round(g)):02x}{int(round(b)):02x}"
        return None

    def _extract_stroke(self, layer) -> Tuple[Optional[str], float]:
        """Extract stroke color and stroke width."""
        stroke = getattr(layer, "stroke", None)
        if not stroke or not getattr(stroke, "enabled", False):
            return None, 0.0

        width = float(getattr(stroke, "line_width", 0.0) or getattr(stroke, "width", 0.0) or 0.0)
        color = None
        # Try extracting stroke fill color if present
        content = getattr(stroke, "content", None)
        if content:
            clr = self._find_color_in_dict(content)
            if clr:
                color = clr

        return color, width
