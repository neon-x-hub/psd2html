"""JSON exporter: serializes LayoutDocument to structured JSON."""

import json
from pathlib import Path
from typing import Union
from ..core.models import LayoutDocument


class JSONExporter:
    """Serializes layout document into clean, framework-independent JSON."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def to_json(self, document: LayoutDocument) -> str:
        """Convert LayoutDocument to a formatted JSON string."""
        return json.dumps(document.to_dict(), indent=self.indent, ensure_ascii=False)

    def export_file(self, document: LayoutDocument, output_path: Union[str, Path]) -> Path:
        """Write JSON output to a file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.to_json(document)
        path.write_text(content, encoding="utf-8")
        return path
