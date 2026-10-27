"""HTML and CSS generation engine."""

from pathlib import Path
from typing import Dict, List, Tuple, Union
from ..core.models import LayoutDocument, LayoutNode


class HTMLCSSGenerator:
    """Generates semantic HTML and modern CSS from a LayoutDocument."""

    def __init__(self, include_comments: bool = True):
        self.include_comments = include_comments

    def generate_css(self, document: LayoutDocument) -> str:
        """Generate CSS stylesheet with rules for each node in the layout tree."""
        css_lines: List[str] = [
            "/* Reset & Base Styles */",
            "*, *::before, *::after {",
            "  box-sizing: border-box;",
            "  margin: 0;",
            "  padding: 0;",
            "}",
            "",
            "body {",
            "  min-height: 100vh;",
            "  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
            "  background-color: #ffffff;",
            "}",
            "",
            "/* Layout Elements */",
        ]

        rules_map: Dict[str, Dict[str, str]] = {}
        self._collect_css_rules(document.root_node, rules_map)

        for selector, styles in rules_map.items():
            css_lines.append(f"{selector} {{")
            for prop, val in styles.items():
                css_lines.append(f"  {prop}: {val};")
            css_lines.append("}")
            css_lines.append("")

        return "\n".join(css_lines)

    def _collect_css_rules(self, node: LayoutNode, rules_map: Dict[str, Dict[str, str]]):
        """Recursively collects CSS properties for every node."""
        selector = f".{node.css_class}"
        if selector not in rules_map:
            rules_map[selector] = dict(node.styles)
        else:
            # If class name collision, use id
            id_selector = f"#{node.id}"
            rules_map[id_selector] = dict(node.styles)

        for child in node.children:
            self._collect_css_rules(child, rules_map)

    def generate_html_body(self, node: LayoutNode, depth: int = 2) -> str:
        """Recursively generate semantic HTML markup for a node."""
        indent = "  " * depth
        tag = node.html_tag
        css_class = node.css_class
        node_id = node.id

        comment = f" <!-- {node.name} -->" if self.include_comments else ""

        if not node.children:
            return f'{indent}<{tag} id="{node_id}" class="{css_class}">{comment}</{tag}>'

        lines = [f'{indent}<{tag} id="{node_id}" class="{css_class}">{comment}']
        for child in node.children:
            lines.append(self.generate_html_body(child, depth + 1))
        lines.append(f"{indent}</{tag}>")
        return "\n".join(lines)

    def generate_standalone(self, document: LayoutDocument) -> str:
        """Generate a complete standalone HTML document with embedded CSS."""
        css = self.generate_css(document)
        body_content = self.generate_html_body(document.root_node, depth=1)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{document.canvas_name} - PSD2HTML Preview</title>
  <style>
{css}
  </style>
</head>
<body>
{body_content}
</body>
</html>
"""

    def generate_html_file(self, document: LayoutDocument, css_filename: str = "styles.css") -> str:
        """Generate HTML referencing an external CSS file."""
        body_content = self.generate_html_body(document.root_node, depth=1)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{document.canvas_name} - PSD2HTML</title>
  <link rel="stylesheet" href="{css_filename}">
</head>
<body>
{body_content}
</body>
</html>
"""

    def export_files(
        self,
        document: LayoutDocument,
        output_dir: Union[str, Path],
        standalone: bool = True,
    ) -> Tuple[Path, Path]:
        """Export HTML and CSS files to the output directory."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        html_path = out_path / "index.html"
        css_path = out_path / "styles.css"

        css_content = self.generate_css(document)
        css_path.write_text(css_content, encoding="utf-8")

        if standalone:
            html_content = self.generate_standalone(document)
        else:
            html_content = self.generate_html_file(document, css_filename="styles.css")

        html_path.write_text(html_content, encoding="utf-8")
        return html_path, css_path
