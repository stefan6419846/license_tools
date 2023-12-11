# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import datetime
from collections import OrderedDict
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import mock, TestCase

from license_tools import font_tools
from tests.data import get_file


class ConvertHeadFlagsTestCase(TestCase):
    def test_none(self) -> None:
        self.assertEqual("%", font_tools.convert_head_flags(0))

    def test_all(self) -> None:
        self.assertEqual(
            (
                "Baseline for font at y=0; "
                "Left sidebearing point at x=0; "
                "Instructions may depend on point size; "
                "Force ppem to integer values; "
                "Instructions may alter advance width; "
                "Lossless font data; "
                "Font converted; "
                "Font optimized for ClearType; "
                "Last Resort font"
            ),
            font_tools.convert_head_flags(2**16 - 1),
        )

    def test_some(self) -> None:
        self.assertEqual(
            "Baseline for font at y=0; " "Font converted",
            font_tools.convert_head_flags(1 + 2**12),
        )


class ConvertTimestamp(TestCase):
    def test_convert_timestamp(self) -> None:
        self.assertEqual(
            datetime.datetime(year=2023, month=12, day=3, hour=4, minute=8, second=57, tzinfo=datetime.timezone.utc),
            font_tools.convert_timestamp_to_datetime(3784421337),
        )
        self.assertEqual(
            "2023-11-29 20:15:42", font_tools.convert_timestamp_to_string(3784133742)
        )
        self.assertEqual(
            "1904-01-01 00:00:00", font_tools.convert_timestamp_to_string(-1)
        )


class ConvertMacStyleTestCase(TestCase):
    def test_none(self) -> None:
        self.assertEqual("%", font_tools.convert_mac_style(0))

    def test_all(self) -> None:
        self.assertEqual(
            "Bold, Italic, Underline, Outline, Shadow, Condensed, Extended",
            font_tools.convert_mac_style(2 ** 7 - 1),
        )

    def test_some(self) -> None:
        self.assertEqual(
            "Bold, Italic, Condensed", font_tools.convert_mac_style(1 + 2 + 32)
        )


class ConvertFontDirectionHintTestCase(TestCase):
    def test_convert_font_direction_hint(self) -> None:
        self.assertEqual(
            "Fully mixed directional glyphs", font_tools.convert_font_direction_hint(0)
        )
        self.assertEqual(
            "Only strongly left to right", font_tools.convert_font_direction_hint(1)
        )
        self.assertEqual(
            "Strongly right to left, but also contains neutrals",
            font_tools.convert_font_direction_hint(-2),
        )


class ConvertLocFormatTestCase(TestCase):
    def test_convert_loc_format(self) -> None:
        self.assertEqual("Long offsets (Offset32)", font_tools.convert_loc_format(1))


class IdentityTestCase(TestCase):
    def test_identity(self) -> None:
        self.assertEqual(42, font_tools.identity(42))
        self.assertEqual("test", font_tools.identity("test"))
        obj = object()
        self.assertEqual(obj, font_tools.identity(obj))


class AnalyzeFontTestCase(TestCase):
    def test_no_known_font_type(self) -> None:
        with get_file("LICENSE.md") as path:
            self.assertIsNone(font_tools.analyze_font(path))

    def test_ttf_file(self) -> None:
        with get_file("Carlito-Regular.ttf") as path:
            result = font_tools.analyze_font(path)

        self.assertEqual(
            {
                "head": OrderedDict(
                    [
                        ("Font Table Version", 1.0),
                        ("Font Revision", 1.10400390625),
                        ("Checksum", 1913909807),
                        ("Magic number", 1594834165),
                        (
                            "Flags",
                            "Baseline for font at y=0; Left sidebearing point at x=0; Force ppem to integer values; Instructions may alter advance width",
                        ),
                        ("Units per em", 2048),
                        ("Created", "2009-07-07 22:19:06"),
                        ("Modified", "2023-02-28 11:34:38"),
                        ("xMin", -1002),
                        ("yMin", -529),
                        ("xMax", 2351),
                        ("yMax", 2078),
                        ("Mac Style", "%"),
                        ("Smallest readable size in pixels", 6),
                        ("Font direction hint", "Strongly left to right, but also contains neutrals"),
                        ("Index to Loc format", "Long offsets (Offset32)"),
                        ("Glyph Data Format", 0),
                    ]
                ),
                "name": OrderedDict(
                    [
                        ("Copyright notice", "Copyright 2013 The Carlito Project Authors (https://github.com/googlefonts/carlito)"),
                        ("Font family name", "Carlito"),
                        ("Font subfamily name", "Regular"),
                        ("Unique font identifier", "1.104;tyPL;Carlito-Regular"),
                        ("Full font name", "Carlito Regular"),
                        ("Version string", "Version 1.104"),
                        ("PostScript name", "Carlito-Regular"),
                        ("Trademark", "Carlito is a trademark of tyPoland Lukasz Dziedzic."),
                        ("Manufacturer", "tyPoland Lukasz Dziedzic"),
                        ("Designer", "Lukasz Dziedzic"),
                        ("Description", "Carlito is a sanserif typeface family based on Lato."),
                        ("URL Vendor", "http://www.lukaszdziedzic.eu"),
                        ("URL Designer", "http://www.lukaszdziedzic.eu"),
                        (
                            "License Description",
                            (
                                "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                                "This license is available with a FAQ at: https://scripts.sil.org/OFL"
                            ),
                        ),
                        ("License Info URL", "https://scripts.sil.org/OFL"),
                    ]
                ),
            },
            result,
        )

    def test_woff_file(self) -> None:
        with get_file("weathericons-regular-webfont.woff") as path:
            result = font_tools.analyze_font(path)

        self.assertEqual(
            {
                "head": OrderedDict(
                    [
                        ("Font Table Version", 1.0),
                        ("Font Revision", 1.0999908447265625),
                        ("Checksum", 339860824),
                        ("Magic number", 1594834165),
                        (
                            "Flags",
                            (
                                "Baseline for font at y=0; Left sidebearing point at x=0; Instructions may depend on point size; "
                                "Force ppem to integer values; Instructions may alter advance width"
                            ),
                        ),
                        ("Units per em", 2048),
                        ("Created", "2015-08-18 21:25:12"),
                        ("Modified", "2015-08-18 21:25:12"),
                        ("xMin", -10),
                        ("yMin", -678),
                        ("xMax", 3133),
                        ("yMax", 2245),
                        ("Mac Style", "%"),
                        ("Smallest readable size in pixels", 8),
                        ("Font direction hint", "Strongly left to right, but also contains neutrals"),
                        ("Index to Loc format", "Short offsets (Offset16)"),
                        ("Glyph Data Format", 0),
                    ]
                ),
                "name": OrderedDict(
                    [
                        (
                            "Copyright notice",
                            "Weather Icons licensed under SIL OFL 1.1 — Code licensed under MIT License — Documentation licensed under CC BY 3.0",
                        ),
                        ("Font family name", "Weather Icons"),
                        ("Font subfamily name", "Regular"),
                        ("Unique font identifier", "1.100;UKWN;WeatherIcons-Regular"),
                        ("Full font name", "Weather Icons Regular"),
                        ("Version string", "Version 1.100;PS 001.100;hotconv 1.0.70;makeotf.lib2.5.58329"),
                        ("PostScript name", "WeatherIcons-Regular"),
                        ("Designer", "Erik Flowers, Lukas Bischoff (v1 Art)"),
                        ("URL Designer", "http://www.helloerik.com, http://www.artill.de"),
                    ]
                ),
            },
            result,
        )

    def test_woff2_file(self) -> None:
        with get_file("fa-solid-900.woff2") as path:
            result = font_tools.analyze_font(path)

        self.assertEqual(
            {
                "head": OrderedDict(
                    [
                        ("Font Table Version", 1.0),
                        ("Font Revision", 773.01171875),
                        ("Checksum", 1882611267),
                        ("Magic number", 1594834165),
                        ("Flags", "Baseline for font at y=0; Left sidebearing point at x=0; Force ppem to integer values"),
                        ("Units per em", 512),
                        ("Created", "2023-11-29 22:28:05"),
                        ("Modified", "2023-11-29 22:28:05"),
                        ("xMin", -13),
                        ("yMin", -75),
                        ("xMax", 651),
                        ("yMax", 459),
                        ("Mac Style", "%"),
                        ("Smallest readable size in pixels", 8),
                        ("Font direction hint", "Strongly left to right, but also contains neutrals"),
                        ("Index to Loc format", "Long offsets (Offset32)"),
                        ("Glyph Data Format", 0),
                    ]
                ),
                "name": OrderedDict(
                    [
                        ("Copyright notice", "Copyright (c) Font Awesome"),
                        ("Font family name", "Font Awesome 6 Free Solid"),
                        ("Font subfamily name", "Solid"),
                        ("Unique font identifier", "Font Awesome 6 Free Solid-6.5.1"),
                        ("Full font name", "Font Awesome 6 Free Solid"),
                        ("Version string", "Version 773.01171875 (Font Awesome version: 6.5.1)"),
                        ("PostScript name", "FontAwesome6Free-Solid"),
                        ("Description", "The web's most popular icon set and toolkit."),
                        ("URL Vendor", "https://fontawesome.com"),
                        ("Typographic Family name", "Font Awesome 6 Free"),
                        ("Typographic Subfamily name", "Solid"),
                    ]
                ),
            },
            result,
        )


class CheckFontTestCase(TestCase):
    def test_no_known_font_type(self) -> None:
        with get_file("LICENSE.md") as path:
            self.assertIsNone(font_tools.check_font(path))

    def test_no_names(self) -> None:
        reference = font_tools.analyze_font

        def analyze_font(path: Path) -> dict[str, None | dict[str, font_tools.FONT_VALUE_TYPE]] | None:
            _result = reference(path)
            _result["name"] = None  # type: ignore[index]
            return _result

        with get_file("Carlito-Regular.ttf") as ttf_path, \
                mock.patch.object(font_tools, "analyze_font", side_effect=analyze_font):
            result = font_tools.check_font(ttf_path)
        self.assertIsNone(result)

    def test_valid(self) -> None:
        with get_file("fa-solid-900.woff2") as path:
            result = font_tools.check_font(path)
        # Important note: The output does not end with a newline!
        self.assertEqual(
            """
          Copyright notice: Copyright (c) Font Awesome
          Font family name: Font Awesome 6 Free Solid
       Font subfamily name: Solid
    Unique font identifier: Font Awesome 6 Free Solid-6.5.1
            Full font name: Font Awesome 6 Free Solid
            Version string: Version 773.01171875 (Font Awesome version: 6.5.1)
           PostScript name: FontAwesome6Free-Solid
               Description: The web's most popular icon set and toolkit.
                URL Vendor: https://fontawesome.com
   Typographic Family name: Font Awesome 6 Free
Typographic Subfamily name: Solid"""[1:],
            result
        )


class DumpToTtxTestCase(TestCase):
    def test_dump_to_ttx(self) -> None:
        with get_file("Carlito-Regular.ttf") as path:
            with NamedTemporaryFile(suffix=".ttx") as target:
                target_path = Path(target.name)
                result = font_tools.dump_to_ttx(source_path=path, target_path=target_path)
                self.assertEqual(target_path, result)

                # Due to the obligation of the OFL-1.1, do not compare against the actual
                # content here. TTX files can be considered a format conversion and thus
                # would require not using the `Carlito` name if we would ship the
                # corresponding target files. A size comparison should be sufficient
                # for now.
                actual = target_path.read_text()
                self.assertLessEqual(9627200, len(actual))  # Tests showed 9627208.
