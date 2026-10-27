"""PSD to HTML Layout Converter (PSD2HTML).

A lightweight, deterministic Photoshop-to-HTML/CSS and JSON layout compiler.
"""

from .core.models import (
    BoundingBox,
    CanvasMode,
    ComputedCoordinates,
    LayoutDocument,
    LayoutNode,
    ParsedMetadata,
    RawLayer,
    SizeMode,
    XPosMode,
    YPosMode,
)
from .core.metadata_parser import MetadataParser
from .core.psd_parser import PSDParser
from .core.layout_resolver import LayoutResolver
from .exporters.json_exporter import JSONExporter
from .exporters.html_generator import HTMLCSSGenerator

__version__ = "0.1.0"

__all__ = [
    "BoundingBox",
    "CanvasMode",
    "ComputedCoordinates",
    "HTMLCSSGenerator",
    "JSONExporter",
    "LayoutDocument",
    "LayoutNode",
    "LayoutResolver",
    "MetadataParser",
    "PSDParser",
    "ParsedMetadata",
    "RawLayer",
    "SizeMode",
    "XPosMode",
    "YPosMode",
    "__version__",
]
