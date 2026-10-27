"""Parser for PSD layer names and layout utility notation."""

import re
from typing import Optional, List, Dict
from .models import (
    ParsedMetadata,
    SizeMode,
    XPosMode,
    YPosMode,
)

# Semantic HTML tag mapping for common layout element names
SEMANTIC_TAG_MAPPING = {
    "header": "header",
    "navbar": "nav",
    "nav": "nav",
    "navigation": "nav",
    "sidebar": "aside",
    "aside": "aside",
    "main": "main",
    "content": "main",
    "footer": "footer",
    "section": "section",
    "article": "article",
    "button": "button",
    "btn": "button",
    "logo": "div",
}


class MetadataParser:
    """Parses layer name metadata into a structured ParsedMetadata object."""

    @staticmethod
    def parse(layer_name: str) -> ParsedMetadata:
        """Parse a layer name formatted as 'Name | token1 token2 ...'."""
        if not layer_name:
            return ParsedMetadata(raw_name="", clean_name="layer")

        raw_name = layer_name.strip()

        # Split into name and metadata tokens
        if "|" in raw_name:
            parts = raw_name.split("|", 1)
            name_part = parts[0].strip()
            tokens_part = parts[1].strip()
            tokens = [t.strip() for t in tokens_part.split() if t.strip()]
        else:
            name_part = raw_name
            tokens = []

        is_container = (name_part == "#" or name_part.startswith("#"))
        clean_name = name_part if name_part else ("container" if is_container else "layer")

        width_mode = SizeMode.ABS
        height_mode = SizeMode.ABS
        x_mode = XPosMode.LEFT_ABS
        y_mode = YPosMode.TOP_ABS
        display = None
        position = "absolute"
        html_tag = None
        classes: List[str] = []
        custom_props: Dict[str, str] = {}

        for token in tokens:
            token_lower = token.lower()

            # Dimension modes
            if token_lower == "w-abs":
                width_mode = SizeMode.ABS
            elif token_lower == "w-rel":
                width_mode = SizeMode.REL
            elif token_lower == "h-abs":
                height_mode = SizeMode.ABS
            elif token_lower == "h-rel":
                height_mode = SizeMode.REL

            # X Position modes
            elif token_lower in ("left-abs", "x-abs"):
                x_mode = XPosMode.LEFT_ABS if token_lower == "left-abs" else XPosMode.X_ABS
            elif token_lower in ("left-rel", "x-rel"):
                x_mode = XPosMode.LEFT_REL if token_lower == "left-rel" else XPosMode.X_REL
            elif token_lower == "right-abs":
                x_mode = XPosMode.RIGHT_ABS
            elif token_lower == "right-rel":
                x_mode = XPosMode.RIGHT_REL

            # Y Position modes
            elif token_lower in ("top-abs", "y-abs"):
                y_mode = YPosMode.TOP_ABS if token_lower == "top-abs" else YPosMode.Y_ABS
            elif token_lower in ("top-rel", "y-rel"):
                y_mode = YPosMode.TOP_REL if token_lower == "top-rel" else YPosMode.Y_REL
            elif token_lower == "bottom-abs":
                y_mode = YPosMode.BOTTOM_ABS
            elif token_lower == "bottom-rel":
                y_mode = YPosMode.BOTTOM_REL

            # Positioning mode
            elif token_lower == "pos-rel":
                position = "relative"
            elif token_lower == "pos-abs":
                position = "absolute"
            elif token_lower == "pos-fixed":
                position = "fixed"

            # Display mode
            elif token_lower in ("flex", "display-flex"):
                display = "flex"
            elif token_lower in ("grid", "display-grid"):
                display = "grid"
            elif token_lower in ("block", "display-block"):
                display = "block"
            elif token_lower == "flex-col":
                display = "flex"
                custom_props["flex-direction"] = "column"
            elif token_lower == "flex-row":
                display = "flex"
                custom_props["flex-direction"] = "row"

            # Alignment / Justification
            elif token_lower == "items-center":
                custom_props["align-items"] = "center"
            elif token_lower == "items-start":
                custom_props["align-items"] = "flex-start"
            elif token_lower == "items-end":
                custom_props["align-items"] = "flex-end"
            elif token_lower == "justify-between":
                custom_props["justify-content"] = "space-between"
            elif token_lower == "justify-center":
                custom_props["justify-content"] = "center"
            elif token_lower == "justify-start":
                custom_props["justify-content"] = "flex-start"
            elif token_lower == "justify-end":
                custom_props["justify-content"] = "flex-end"

            # Gap (e.g. gap-10 or gap-16px)
            elif token_lower.startswith("gap-"):
                gap_val = token_lower[4:]
                if gap_val.isdigit():
                    gap_val += "px"
                custom_props["gap"] = gap_val

            # Explicit tag token (e.g. tag-header, tag-nav)
            elif token_lower.startswith("tag-"):
                html_tag = token_lower[4:]

            # Class token (e.g. class-name or .class-name)
            elif token_lower.startswith("class-"):
                classes.append(token[6:])
            elif token.startswith("."):
                classes.append(token[1:])

            # Arbitrary property: key-val (e.g. z-10)
            elif "-" in token:
                classes.append(token)

        # Infer HTML tag if not explicitly set
        if not html_tag:
            name_normalized = re.sub(r"[^a-zA-Z0-9]", "", clean_name).lower()
            for key, tag in SEMANTIC_TAG_MAPPING.items():
                if key in name_normalized:
                    html_tag = tag
                    break
            if not html_tag:
                html_tag = "div"

        return ParsedMetadata(
            raw_name=raw_name,
            clean_name=clean_name,
            is_container=is_container,
            width_mode=width_mode,
            height_mode=height_mode,
            x_mode=x_mode,
            y_mode=y_mode,
            display=display,
            position=position,
            html_tag=html_tag,
            classes=classes,
            custom_props=custom_props,
        )
