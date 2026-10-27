"""Test package metadata, top-level exports, and CLI functionality."""

import subprocess
import sys
import unittest
import psd2html
from psd2html import (
    BoundingBox,
    CanvasMode,
    HTMLCSSGenerator,
    JSONExporter,
    LayoutDocument,
    LayoutNode,
    LayoutResolver,
    MetadataParser,
    PSDParser,
    SizeMode,
    __version__,
)


class TestPackage(unittest.TestCase):
    def test_version_present(self):
        self.assertTrue(__version__)
        self.assertEqual(psd2html.__version__, "0.1.0")

    def test_top_level_exports(self):
        self.assertIsNotNone(PSDParser)
        self.assertIsNotNone(LayoutResolver)
        self.assertIsNotNone(HTMLCSSGenerator)
        self.assertIsNotNone(JSONExporter)
        self.assertIsNotNone(MetadataParser)
        self.assertIsNotNone(BoundingBox)
        self.assertIsNotNone(LayoutNode)
        self.assertIsNotNone(LayoutDocument)
        self.assertIsNotNone(CanvasMode)
        self.assertIsNotNone(SizeMode)

    def test_cli_version_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "psd2html", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("psd2html 0.1.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
