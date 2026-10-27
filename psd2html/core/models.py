"""Data models for PSD2HTML layout extraction, representation, and export."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class SizeMode(str, Enum):
    """Dimension interpretation mode."""
    ABS = "abs"
    REL = "rel"


class CanvasMode(str, Enum):
    """Artboard / Canvas sizing mode."""
    VIEWPORT = "viewport"  # Responsive to viewport size (default)
    FIXED = "fixed"        # Strictly fixed to PSD artboard pixel dimensions


class XPosMode(str, Enum):
    """Horizontal position interpretation mode."""
    LEFT_ABS = "left-abs"
    LEFT_REL = "left-rel"
    RIGHT_ABS = "right-abs"
    RIGHT_REL = "right-rel"
    X_ABS = "x-abs"  # Defaults to left-abs
    X_REL = "x-rel"  # Defaults to left-rel


class YPosMode(str, Enum):
    """Vertical position interpretation mode."""
    TOP_ABS = "top-abs"
    TOP_REL = "top-rel"
    BOTTOM_ABS = "bottom-abs"
    BOTTOM_REL = "bottom-rel"
    Y_ABS = "y-abs"  # Defaults to top-abs
    Y_REL = "y-rel"  # Defaults to top-rel


@dataclass
class BoundingBox:
    """Bounding box in pixel coordinates."""
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return max(0.0, self.right - self.left)

    @property
    def height(self) -> float:
        return max(0.0, self.bottom - self.top)

    def to_dict(self) -> Dict[str, float]:
        return {
            "left": round(self.left, 2),
            "top": round(self.top, 2),
            "right": round(self.right, 2),
            "bottom": round(self.bottom, 2),
            "width": round(self.width, 2),
            "height": round(self.height, 2),
        }


@dataclass
class ParsedMetadata:
    """Metadata parsed from Photoshop layer name."""
    raw_name: str
    clean_name: str
    is_container: bool = False  # True if name represents group container (#)
    width_mode: SizeMode = SizeMode.ABS
    height_mode: SizeMode = SizeMode.ABS
    x_mode: XPosMode = XPosMode.LEFT_ABS
    y_mode: YPosMode = YPosMode.TOP_ABS
    display: Optional[str] = None  # e.g., 'flex', 'grid', 'block'
    position: str = "absolute"     # 'absolute' or 'relative' (pos-rel)
    html_tag: Optional[str] = None # e.g. 'header', 'nav', 'aside', 'main'
    classes: List[str] = field(default_factory=list)
    custom_props: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_name": self.raw_name,
            "clean_name": self.clean_name,
            "is_container": self.is_container,
            "width_mode": self.width_mode.value,
            "height_mode": self.height_mode.value,
            "x_mode": self.x_mode.value,
            "y_mode": self.y_mode.value,
            "display": self.display,
            "position": self.position,
            "html_tag": self.html_tag,
            "classes": self.classes,
            "custom_props": self.custom_props,
        }


@dataclass
class RawLayer:
    """Raw layer information extracted from PSD."""
    name: str
    kind: str
    bbox: BoundingBox
    visible: bool = True
    opacity: float = 1.0
    fill_color: Optional[str] = None    # Hex string, e.g., '#fdc9a9'
    stroke_color: Optional[str] = None  # Hex string
    stroke_width: float = 0.0
    metadata: Optional[ParsedMetadata] = None
    children: List[RawLayer] = field(default_factory=list)


@dataclass
class ComputedCoordinates:
    """Calculated absolute or relative CSS dimension and position values."""
    width: str
    height: str
    horizontal_prop: str   # 'left' or 'right'
    horizontal_value: str  # e.g., '15px' or '12.5%'
    vertical_prop: str     # 'top' or 'bottom'
    vertical_value: str    # e.g., '10px' or '2.4%'

    def to_dict(self) -> Dict[str, str]:
        return {
            "width": self.width,
            "height": self.height,
            "horizontal_prop": self.horizontal_prop,
            "horizontal_value": self.horizontal_value,
            "vertical_prop": self.vertical_prop,
            "vertical_value": self.vertical_value,
        }


@dataclass
class LayoutNode:
    """A resolved node in the layout tree."""
    id: str
    name: str
    html_tag: str
    css_class: str
    raw_bbox: BoundingBox
    computed: ComputedCoordinates
    styles: Dict[str, str] = field(default_factory=dict)
    metadata: Optional[ParsedMetadata] = None
    children: List[LayoutNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "html_tag": self.html_tag,
            "css_class": self.css_class,
            "raw_bbox": self.raw_bbox.to_dict(),
            "computed": self.computed.to_dict(),
            "styles": self.styles,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class LayoutDocument:
    """Root document representing the converted layout."""
    canvas_name: str
    canvas_width: int
    canvas_height: int
    root_node: LayoutNode
    canvas_mode: CanvasMode = CanvasMode.VIEWPORT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canvas_name": self.canvas_name,
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "canvas_mode": self.canvas_mode.value,
            "root_node": self.root_node.to_dict(),
        }
