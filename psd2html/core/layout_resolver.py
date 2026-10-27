"""Layout resolver module: converts raw PSD layers into resolved layout nodes."""

import re
from typing import List, Optional, Tuple
from .models import (
    BoundingBox,
    RawLayer,
    LayoutNode,
    LayoutDocument,
    ComputedCoordinates,
    ParsedMetadata,
    SizeMode,
    CanvasMode,
    XPosMode,
    YPosMode,
)
from .metadata_parser import MetadataParser


def slugify(text: str) -> str:
    """Convert layer name to a valid CSS class name (kebab-case)."""
    text = re.sub(r"[^\w\s-]", "", text.strip()).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text or "item"


def format_px(val: float) -> str:
    """Format pixel value cleanly."""
    rounded = round(val)
    if abs(val - rounded) < 0.05:
        return f"{int(rounded)}px"
    return f"{val:.2f}px"


def format_pct(val: float) -> str:
    """Format percentage value cleanly."""
    rounded = round(val, 2)
    if rounded == int(rounded):
        return f"{int(rounded)}%"
    return f"{rounded:.2f}%"


class LayoutResolver:
    """Resolves layer hierarchy, '#' parent container semantics, and coordinates."""

    def __init__(
        self,
        canvas_mode: CanvasMode | str = CanvasMode.VIEWPORT,
        clamp_negative_coords: bool = True,
    ):
        if isinstance(canvas_mode, str):
            canvas_mode = CanvasMode(canvas_mode.lower())
        self.canvas_mode = canvas_mode
        self.clamp_negative_coords = clamp_negative_coords
        self._id_counter = 0

    def resolve(self, canvas_bbox: BoundingBox, raw_root: RawLayer) -> LayoutDocument:
        """Resolve a full RawLayer tree into a LayoutDocument."""
        self._id_counter = 0

        # If canvas top-left has negative offset, normalize canvas bounding box
        normalized_canvas_bbox = BoundingBox(
            left=0.0,
            top=0.0,
            right=canvas_bbox.width,
            bottom=canvas_bbox.height,
        )

        root_node = self._resolve_node(
            raw_layer=raw_root,
            parent_bbox=normalized_canvas_bbox,
            is_root=True,
        )

        return LayoutDocument(
            canvas_name=raw_root.name,
            canvas_width=int(round(canvas_bbox.width)),
            canvas_height=int(round(canvas_bbox.height)),
            canvas_mode=self.canvas_mode,
            root_node=root_node,
        )

    def _next_id(self, prefix: str) -> str:
        self._id_counter += 1
        return f"{prefix}-{self._id_counter}"

    def _resolve_node(
        self,
        raw_layer: RawLayer,
        parent_bbox: BoundingBox,
        is_root: bool = False,
    ) -> LayoutNode:
        """Resolve a single RawLayer and its children relative to parent_bbox."""
        meta = raw_layer.metadata or MetadataParser.parse(raw_layer.name)

        # 1. Check for child '#' container layer inside this group
        container_child, non_container_children = self._extract_container_layer(raw_layer.children)

        # 2. Determine effective geometry and styling for this node
        effective_bbox = raw_layer.bbox
        fill_color = raw_layer.fill_color
        stroke_color = raw_layer.stroke_color
        stroke_width = raw_layer.stroke_width

        # If this group has an explicit '#' container child, inherit its geometry and styles
        if container_child:
            effective_bbox = container_child.bbox
            if container_child.fill_color:
                fill_color = container_child.fill_color
            if container_child.stroke_color:
                stroke_color = container_child.stroke_color
                stroke_width = container_child.stroke_width
            # Inherit container metadata layout rules if parent didn't specify them
            if container_child.metadata:
                c_meta = container_child.metadata
                meta.width_mode = c_meta.width_mode
                meta.height_mode = c_meta.height_mode
                meta.x_mode = c_meta.x_mode
                meta.y_mode = c_meta.y_mode
                if c_meta.display:
                    meta.display = c_meta.display

        # 3. Calculate computed dimensions and coordinates
        computed = self._compute_coordinates(effective_bbox, parent_bbox, meta, is_root)

        # 4. Generate CSS styles dictionary
        styles = self._build_styles(
            computed=computed,
            meta=meta,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            opacity=raw_layer.opacity,
            has_children=bool(non_container_children),
            is_root=is_root,
        )

        css_class = slugify(meta.clean_name)
        node_id = self._next_id(css_class)
        html_tag = meta.html_tag or ("main" if is_root else "div")

        # 5. Resolve children relative to THIS node's bounding box
        resolved_children: List[LayoutNode] = []
        for child_layer in non_container_children:
            child_node = self._resolve_node(
                raw_layer=child_layer,
                parent_bbox=effective_bbox,
                is_root=False,
            )
            resolved_children.append(child_node)

        return LayoutNode(
            id=node_id,
            name=meta.clean_name,
            html_tag=html_tag,
            css_class=css_class,
            raw_bbox=effective_bbox,
            computed=computed,
            styles=styles,
            metadata=meta,
            children=resolved_children,
        )

    def _extract_container_layer(
        self, children: List[RawLayer]
    ) -> Tuple[Optional[RawLayer], List[RawLayer]]:
        """Separate '#' container layer from other sibling layers."""
        container = None
        others = []
        for child in children:
            if child.metadata and child.metadata.is_container and container is None:
                container = child
            elif child.name.strip() == "#" and container is None:
                container = child
            else:
                others.append(child)
        return container, others

    def _compute_coordinates(
        self,
        bbox: BoundingBox,
        parent_bbox: BoundingBox,
        meta: ParsedMetadata,
        is_root: bool,
    ) -> ComputedCoordinates:
        """Compute dimensions and coordinates using absolute or relative rules."""
        parent_w = max(1.0, parent_bbox.width)
        parent_h = max(1.0, parent_bbox.height)

        # --- Width ---
        if is_root:
            if self.canvas_mode == CanvasMode.VIEWPORT:
                width_str = "100%"
            else:
                width_str = format_px(bbox.width)
        elif meta.width_mode == SizeMode.REL:
            width_pct = (bbox.width / parent_w) * 100.0
            width_str = format_pct(width_pct)
        else:
            width_str = format_px(bbox.width)

        # --- Height ---
        if is_root:
            if self.canvas_mode == CanvasMode.VIEWPORT:
                height_str = "100vh"
            else:
                height_str = format_px(bbox.height)
        elif meta.height_mode == SizeMode.REL:
            height_pct = (bbox.height / parent_h) * 100.0
            height_str = format_pct(height_pct)
        else:
            height_str = format_px(bbox.height)

        # --- Horizontal Position (X) ---
        # Options: left-abs, left-rel, right-abs, right-rel, x-abs, x-rel
        x_mode = meta.x_mode
        if x_mode in (XPosMode.RIGHT_ABS, XPosMode.RIGHT_REL):
            horiz_prop = "right"
            raw_right_offset = parent_bbox.right - bbox.right
            if self.clamp_negative_coords and raw_right_offset < 0:
                raw_right_offset = 0.0

            if x_mode == XPosMode.RIGHT_REL:
                horiz_val = format_pct((raw_right_offset / parent_w) * 100.0)
            else:
                horiz_val = format_px(raw_right_offset)
        else:
            # Default to left alignment
            horiz_prop = "left"
            raw_left_offset = bbox.left - parent_bbox.left
            if self.clamp_negative_coords and raw_left_offset < 0:
                raw_left_offset = 0.0

            if x_mode in (XPosMode.LEFT_REL, XPosMode.X_REL):
                horiz_val = format_pct((raw_left_offset / parent_w) * 100.0)
            else:
                horiz_val = format_px(raw_left_offset)

        # --- Vertical Position (Y) ---
        # Options: top-abs, top-rel, bottom-abs, bottom-rel, y-abs, y-rel
        y_mode = meta.y_mode
        if y_mode in (YPosMode.BOTTOM_ABS, YPosMode.BOTTOM_REL):
            vert_prop = "bottom"
            raw_bottom_offset = parent_bbox.bottom - bbox.bottom
            if self.clamp_negative_coords and raw_bottom_offset < 0:
                raw_bottom_offset = 0.0

            if y_mode == YPosMode.BOTTOM_REL:
                vert_val = format_pct((raw_bottom_offset / parent_h) * 100.0)
            else:
                vert_val = format_px(raw_bottom_offset)
        else:
            # Default to top alignment
            vert_prop = "top"
            raw_top_offset = bbox.top - parent_bbox.top
            if self.clamp_negative_coords and raw_top_offset < 0:
                raw_top_offset = 0.0

            if y_mode in (YPosMode.TOP_REL, YPosMode.Y_REL):
                vert_val = format_pct((raw_top_offset / parent_h) * 100.0)
            else:
                vert_val = format_px(raw_top_offset)

        if is_root:
            horiz_prop = "left"
            horiz_val = "0"
            vert_prop = "top"
            vert_val = "0"

        return ComputedCoordinates(
            width=width_str,
            height=height_str,
            horizontal_prop=horiz_prop,
            horizontal_value=horiz_val,
            vertical_prop=vert_prop,
            vertical_value=vert_val,
        )

    def _build_styles(
        self,
        computed: ComputedCoordinates,
        meta: ParsedMetadata,
        fill_color: Optional[str],
        stroke_color: Optional[str],
        stroke_width: float,
        opacity: float,
        has_children: bool,
        is_root: bool,
    ) -> dict[str, str]:
        """Assemble all CSS properties for this node."""
        styles: dict[str, str] = {}

        # Sizing
        styles["width"] = computed.width
        styles["height"] = computed.height

        # Positioning
        if is_root:
            styles["position"] = "relative"
            if self.canvas_mode == CanvasMode.VIEWPORT:
                styles["width"] = "100%"
                styles["min-height"] = "100vh"
                styles["overflow-x"] = "hidden"
            else:
                styles["width"] = computed.width
                styles["height"] = computed.height
                styles["margin"] = "0 auto"
                styles["overflow"] = "hidden"
        else:
            # If explicit pos-rel, use relative; else if has children, position: relative
            # If child of another container, position absolute unless specified pos-rel
            if meta.position == "relative":
                styles["position"] = "relative"
            elif has_children and meta.position == "absolute":
                # Container that has children positioned absolutely needs position: absolute (or relative)
                # In CSS, absolute containers are also positioned parents for nested absolute children!
                styles["position"] = "absolute"
            else:
                styles["position"] = meta.position

            styles[computed.horizontal_prop] = computed.horizontal_value
            styles[computed.vertical_prop] = computed.vertical_value

        # Display mode
        if meta.display:
            styles["display"] = meta.display

        # Custom layout properties (flex-direction, align-items, etc.)
        for prop, val in meta.custom_props.items():
            styles[prop] = val

        # Colors & Appearance
        if fill_color:
            styles["background-color"] = fill_color

        if stroke_color and stroke_width > 0:
            styles["border"] = f"{format_px(stroke_width)} solid {stroke_color}"

        if opacity < 1.0:
            styles["opacity"] = f"{opacity:.2f}"

        styles["box-sizing"] = "border-box"

        return styles
