"""Unit tests for layout resolver and coordinate math."""

import unittest
from psd2html.core.models import BoundingBox, RawLayer
from psd2html.core.metadata_parser import MetadataParser
from psd2html.core.layout_resolver import LayoutResolver


class TestLayoutResolver(unittest.TestCase):
    def test_relative_dimensions(self):
        canvas_bbox = BoundingBox(0.0, 0.0, 1000.0, 500.0)
        layer = RawLayer(
            name="Banner | w-rel h-rel left-abs top-abs",
            kind="shape",
            bbox=BoundingBox(0.0, 0.0, 500.0, 250.0),
            metadata=MetadataParser.parse("Banner | w-rel h-rel left-abs top-abs"),
        )
        root = RawLayer(
            name="Root",
            kind="canvas",
            bbox=canvas_bbox,
            children=[layer],
        )

        resolver = LayoutResolver()
        doc = resolver.resolve(canvas_bbox, root)
        node = doc.root_node.children[0]

        self.assertEqual(node.computed.width, "50%")
        self.assertEqual(node.computed.height, "50%")
        self.assertEqual(node.computed.horizontal_prop, "left")
        self.assertEqual(node.computed.horizontal_value, "0px")

    def test_right_and_bottom_coordinates(self):
        canvas_bbox = BoundingBox(0.0, 0.0, 1000.0, 500.0)
        layer = RawLayer(
            name="BottomRightBox | w-abs h-abs right-abs bottom-abs",
            kind="shape",
            bbox=BoundingBox(900.0, 450.0, 1000.0, 500.0),
            metadata=MetadataParser.parse("BottomRightBox | w-abs h-abs right-abs bottom-abs"),
        )
        root = RawLayer(
            name="Root",
            kind="canvas",
            bbox=canvas_bbox,
            children=[layer],
        )

        resolver = LayoutResolver()
        doc = resolver.resolve(canvas_bbox, root)
        node = doc.root_node.children[0]

        self.assertEqual(node.computed.width, "100px")
        self.assertEqual(node.computed.height, "50px")
        self.assertEqual(node.computed.horizontal_prop, "right")
        self.assertEqual(node.computed.horizontal_value, "0px")
        self.assertEqual(node.computed.vertical_prop, "bottom")
        self.assertEqual(node.computed.vertical_value, "0px")

    def test_container_hash_resolution(self):
        canvas_bbox = BoundingBox(0.0, 0.0, 1000.0, 500.0)
        container_shape = RawLayer(
            name="# | w-rel h-abs x-abs y-abs",
            kind="shape",
            bbox=BoundingBox(0.0, 0.0, 1000.0, 80.0),
            fill_color="#123456",
            metadata=MetadataParser.parse("# | w-rel h-abs x-abs y-abs"),
        )
        logo = RawLayer(
            name="Logo | w-abs h-abs left-abs top-abs",
            kind="shape",
            bbox=BoundingBox(20.0, 15.0, 70.0, 65.0),
            fill_color="#ffffff",
            metadata=MetadataParser.parse("Logo | w-abs h-abs left-abs top-abs"),
        )
        navbar_group = RawLayer(
            name="Navbar",
            kind="group",
            bbox=BoundingBox(0.0, 0.0, 1000.0, 80.0),
            children=[container_shape, logo],
        )
        root = RawLayer(name="Root", kind="canvas", bbox=canvas_bbox, children=[navbar_group])

        resolver = LayoutResolver()
        doc = resolver.resolve(canvas_bbox, root)

        navbar_node = doc.root_node.children[0]
        # Container shape should be merged into navbar, leaving only Logo as child
        self.assertEqual(navbar_node.name, "Navbar")
        self.assertEqual(navbar_node.styles.get("background-color"), "#123456")
        self.assertEqual(len(navbar_node.children), 1)

        logo_node = navbar_node.children[0]
        self.assertEqual(logo_node.name, "Logo")
        self.assertEqual(logo_node.computed.width, "50px")
        self.assertEqual(logo_node.computed.height, "50px")
        self.assertEqual(logo_node.computed.horizontal_value, "20px")
        self.assertEqual(logo_node.computed.vertical_value, "15px")

    def test_canvas_modes(self):
        canvas_bbox = BoundingBox(0.0, 0.0, 1200.0, 800.0)
        root = RawLayer(name="Root", kind="canvas", bbox=canvas_bbox, children=[])

        # Test Viewport Mode (default)
        resolver_vp = LayoutResolver(canvas_mode="viewport")
        doc_vp = resolver_vp.resolve(canvas_bbox, root)
        self.assertEqual(doc_vp.root_node.styles["width"], "100%")
        self.assertEqual(doc_vp.root_node.styles["min-height"], "100vh")

        # Test Fixed Mode
        resolver_fx = LayoutResolver(canvas_mode="fixed")
        doc_fx = resolver_fx.resolve(canvas_bbox, root)
        self.assertEqual(doc_fx.root_node.styles["width"], "1200px")
        self.assertEqual(doc_fx.root_node.styles["height"], "800px")
        self.assertEqual(doc_fx.root_node.styles["margin"], "0 auto")


if __name__ == "__main__":
    unittest.main()
