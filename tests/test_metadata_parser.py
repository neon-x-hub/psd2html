"""Unit tests for layer metadata parser."""

import unittest
from psd2html.core.metadata_parser import MetadataParser
from psd2html.core.models import SizeMode, XPosMode, YPosMode


class TestMetadataParser(unittest.TestCase):
    def test_container_layer_syntax(self):
        meta = MetadataParser.parse("# | w-rel h-abs x-abs y-abs")
        self.assertTrue(meta.is_container)
        self.assertEqual(meta.clean_name, "#")
        self.assertEqual(meta.width_mode, SizeMode.REL)
        self.assertEqual(meta.height_mode, SizeMode.ABS)
        self.assertEqual(meta.x_mode, XPosMode.X_ABS)
        self.assertEqual(meta.y_mode, YPosMode.Y_ABS)

    def test_logo_syntax(self):
        meta = MetadataParser.parse("Logo | w-abs h-abs right-abs top-rel")
        self.assertFalse(meta.is_container)
        self.assertEqual(meta.clean_name, "Logo")
        self.assertEqual(meta.width_mode, SizeMode.ABS)
        self.assertEqual(meta.height_mode, SizeMode.ABS)
        self.assertEqual(meta.x_mode, XPosMode.RIGHT_ABS)
        self.assertEqual(meta.y_mode, YPosMode.TOP_REL)
        self.assertEqual(meta.html_tag, "div")

    def test_nav_options_syntax(self):
        meta = MetadataParser.parse("Nav Options | w-abs h-abs left-abs y-rel")
        self.assertFalse(meta.is_container)
        self.assertEqual(meta.clean_name, "Nav Options")
        self.assertEqual(meta.width_mode, SizeMode.ABS)
        self.assertEqual(meta.height_mode, SizeMode.ABS)
        self.assertEqual(meta.x_mode, XPosMode.LEFT_ABS)
        self.assertEqual(meta.y_mode, YPosMode.Y_REL)
        self.assertEqual(meta.html_tag, "nav")

    def test_flex_and_alignment(self):
        meta = MetadataParser.parse("Card List | flex flex-row items-center justify-between gap-16")
        self.assertEqual(meta.clean_name, "Card List")
        self.assertEqual(meta.display, "flex")
        self.assertEqual(meta.custom_props["flex-direction"], "row")
        self.assertEqual(meta.custom_props["align-items"], "center")
        self.assertEqual(meta.custom_props["justify-content"], "space-between")
        self.assertEqual(meta.custom_props["gap"], "16px")

    def test_position_relative(self):
        meta = MetadataParser.parse("Header | pos-rel w-rel h-abs")
        self.assertEqual(meta.position, "relative")
        self.assertEqual(meta.width_mode, SizeMode.REL)
        self.assertEqual(meta.height_mode, SizeMode.ABS)
        self.assertEqual(meta.html_tag, "header")

    def test_empty_or_plain_name(self):
        meta = MetadataParser.parse("Simple Layer")
        self.assertEqual(meta.clean_name, "Simple Layer")
        self.assertFalse(meta.is_container)
        self.assertEqual(meta.width_mode, SizeMode.ABS)
        self.assertEqual(meta.height_mode, SizeMode.ABS)


if __name__ == "__main__":
    unittest.main()
