"""End-to-end integration test with example/1.psd."""

import unittest
from pathlib import Path
from psd2html.core.psd_parser import PSDParser
from psd2html.core.layout_resolver import LayoutResolver
from psd2html.exporters.json_exporter import JSONExporter
from psd2html.exporters.html_generator import HTMLCSSGenerator


class TestE2E(unittest.TestCase):
    def setUp(self):
        self.psd_path = Path(__file__).parent.parent / "example" / "1.psd"
        self.output_dir = Path(__file__).parent.parent / "dist"

    def test_full_pipeline_on_example_psd(self):
        self.assertTrue(self.psd_path.exists(), f"Missing test fixture: {self.psd_path}")

        # 1. Parse PSD
        parser = PSDParser(use_vector_geometry=True)
        canvas_bbox, raw_root = parser.parse_file(self.psd_path)

        self.assertEqual(int(canvas_bbox.width), 1366)
        self.assertEqual(int(canvas_bbox.height), 768)

        # 2. Resolve Layout
        resolver = LayoutResolver()
        doc = resolver.resolve(canvas_bbox, raw_root)

        self.assertEqual(doc.canvas_width, 1366)
        self.assertEqual(doc.canvas_height, 768)

        # Check Navbar container
        navbar = doc.root_node.children[0]
        self.assertEqual(navbar.name, "Navbar")
        self.assertEqual(navbar.html_tag, "nav")
        self.assertEqual(navbar.computed.width, "100%")
        self.assertEqual(navbar.styles.get("background-color"), "#fec9a9")

        # Check Logo
        logo = next(c for c in navbar.children if c.name == "Logo")
        self.assertEqual(logo.computed.width, "69px")
        self.assertEqual(logo.computed.height, "69px")
        self.assertEqual(logo.styles.get("background-color"), "#c66c59")

        # Check Nav Options
        nav_options = next(c for c in navbar.children if c.name == "Nav Options")
        self.assertEqual(nav_options.computed.width, "615px")
        self.assertEqual(nav_options.computed.height, "69px")
        self.assertEqual(nav_options.styles.get("background-color"), "#c66c59")

        # 3. JSON Export
        json_exporter = JSONExporter()
        json_out = self.output_dir / "test_1.json"
        json_exporter.export_file(doc, json_out)
        self.assertTrue(json_out.exists())
        self.assertGreater(json_out.stat().st_size, 100)

        # 4. HTML/CSS Export
        html_gen = HTMLCSSGenerator()
        html_out, css_out = html_gen.export_files(doc, self.output_dir, standalone=True)
        self.assertTrue(html_out.exists())
        self.assertTrue(css_out.exists())

        html_text = html_out.read_text(encoding="utf-8")
        self.assertIn("<nav", html_text)
        self.assertIn("navbar", html_text)
        self.assertIn("logo", html_text)
        self.assertIn("nav-options", html_text)
        # Ensure canvas wrapper element was removed
        self.assertNotIn("canvas-wrapper", html_text)

    def test_fixed_mode_pipeline(self):
        parser = PSDParser(use_vector_geometry=True)
        canvas_bbox, raw_root = parser.parse_file(self.psd_path)

        resolver = LayoutResolver(canvas_mode="fixed")
        doc = resolver.resolve(canvas_bbox, raw_root)

        self.assertEqual(doc.canvas_mode.value, "fixed")
        root = doc.root_node
        self.assertEqual(root.styles.get("width"), "1366px")
        self.assertEqual(root.styles.get("height"), "768px")
        self.assertEqual(root.styles.get("margin"), "0 auto")


if __name__ == "__main__":
    unittest.main()
