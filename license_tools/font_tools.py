# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to fonts.
"""

from __future__ import annotations

import datetime
from collections import OrderedDict
from pathlib import Path
from typing import Any, Union

from fontTools import ttx  # type: ignore[import-untyped]
from fontTools.misc import timeTools  # type: ignore[import-untyped]
from fontTools.ttLib import TTFont  # type: ignore[import-untyped]
from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d as HeadTable  # type: ignore[import-untyped]  # noqa: N812
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e as NameTable  # type: ignore[import-untyped]  # noqa: 812


# https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
_TTF_NAME_IDS: list[str] = [
    "Copyright notice",
    "Font family name",
    "Font subfamily name",
    "Unique font identifier",
    "Full font name",
    "Version string",
    "PostScript name",
    "Trademark",
    "Manufacturer",
    "Designer",
    "Description",
    "URL Vendor",
    "URL Designer",
    "License Description",
    "License Info URL",
    "Reserved",
    "Typographic Family name",
    "Typographic Subfamily name",
    "Compatible Full (Mac only)",
    "Sample text",
    "PostScript CID findfont name",
    "WWS Family Name",
    "WWS Subfamily Name",
    "Light Background Palette",
    "Dark Background Palette",
    "Variations PostScript Name Prefix",
]


# https://learn.microsoft.com/en-us/typography/opentype/spec/head
def convert_head_flags(value: int) -> str:
    """
    Convert the given head flags value to a human-readable string.

    :param value: The flags value.
    :return: The corresponding human-readable interpretation.
    """
    result = []
    verbose = [
        "Baseline for font at y=0",
        "Left sidebearing point at x=0",
        "Instructions may depend on point size",
        "Force ppem to integer values",
        "Instructions may alter advance width",
        "",
        "",
        "",
        "",
        "",
        "",
        "Lossless font data",
        "Font converted",
        "Font optimized for ClearType",
        "Last Resort font",
        "",
    ]
    for index, verbose_ in enumerate(verbose):
        if value & (1 << index):
            result.append(verbose_)
    return "; ".join(filter(None, result)) if result else "%"


def convert_timestamp_to_datetime(value: int) -> datetime.datetime:
    """
    Convert the given font timestamp to a datetime object.

    :param value: The font timestamp since the font epoch in 1904.
    :return: The regular datetime object.
    """
    return datetime.datetime.fromtimestamp(
        max(0, value) + timeTools.epoch_diff,
        tz=datetime.timezone.utc
    )


def convert_timestamp_to_string(value: int) -> str:
    """
    Convert the given font timestamp to a string.

    :param value: The font timestamp since the font epoch in 1904.
    :return: The corresponding string representation.
    """
    return convert_timestamp_to_datetime(value).strftime("%Y-%m-%d %H:%M:%S")


def convert_mac_style(value: int) -> str:
    """
    Convert the mac style to a human-readable representation.

    :param value: The style flags.
    :return: The corresponding string representation.
    """
    result = []
    verbose = [
        "Bold",
        "Italic",
        "Underline",
        "Outline",
        "Shadow",
        "Condensed",
        "Extended",
    ]
    for index, verbose_ in enumerate(verbose):
        if value & (1 << index):
            result.append(verbose_)
    return ", ".join(result) if result else "%"


def convert_font_direction_hint(value: int) -> str:
    """
    Convert the given font direction hint to a human-readable representation.

    :param value: The hint value.
    :return: The human-readable representation.
    """
    return {
        0: "Fully mixed directional glyphs",
        1: "Only strongly left to right",
        2: "Strongly left to right, but also contains neutrals",
        -1: "Only strongly right to left",
        -2: "Strongly right to left, but also contains neutrals",
    }[value]


def convert_loc_format(value: int) -> str:
    """
    Convert the given loc value to a human-readable representation.

    :param value: The loc value.
    :return: The human-readable representation.
    """
    return {
        0: "Short offsets (Offset16)",
        1: "Long offsets (Offset32)",
    }[value]


def identity(value: Any) -> Any:
    """
    Utility function to return the value itself.

    :param value: The value to return.
    :return: The input value.
    """
    return value


_TTF_HEAD_IDS = {
    "tableVersion": ("Font Table Version", identity),
    "fontRevision": ("Font Revision", identity),
    "checkSumAdjustment": ("Checksum", identity),
    "magicNumber": ("Magic number", identity),
    "flags": ("Flags", convert_head_flags),
    "unitsPerEm": ("Units per em", identity),
    "created": ("Created", convert_timestamp_to_string),
    "modified": ("Modified", convert_timestamp_to_string),
    "xMin": ("xMin", identity),
    "yMin": ("yMin", identity),
    "xMax": ("xMax", identity),
    "yMax": ("yMax", identity),
    "macStyle": ("Mac Style", convert_mac_style),
    "lowestRecPPEM": ("Smallest readable size in pixels", identity),
    "fontDirectionHint": ("Font direction hint", convert_font_direction_hint),
    "indexToLocFormat": ("Index to Loc format", convert_loc_format),
    "glyphDataFormat": ("Glyph Data Format", identity),
}

KNOWN_FONT_EXTENSIONS = {".ttf", ".woff", ".woff2"}

FONT_VALUE_TYPE = Union[str, int, datetime.datetime]


def handle_ttfont_head(head: HeadTable) -> OrderedDict[str, FONT_VALUE_TYPE]:
    """
    Handle the head section of a TTFont instance.

    :param head: The section to handle.
    :return: The parsed/human-readable mapping.
    """
    result = OrderedDict()
    for key, value in head.__dict__.items():
        if key not in _TTF_HEAD_IDS:
            continue
        identifier, value_parser = _TTF_HEAD_IDS[key]
        parsed_value = value_parser(value)
        result[identifier] = parsed_value
    return result


def handle_ttfont_names(names: NameTable) -> OrderedDict[str, FONT_VALUE_TYPE]:
    """
    Handle the names section of a TTFont instance.

    :param names: The names to handle.
    :return: The parsed/human-readable mapping.
    """
    result = OrderedDict()
    for index, verbose_name in enumerate(_TTF_NAME_IDS):
        name = names.getDebugName(index)
        if name:
            result[verbose_name] = name
    return result


def analyze_font(path: Path) -> dict[str, None | dict[str, FONT_VALUE_TYPE]] | None:
    """
    Analyze the given font and provide a human-readable mapping for the head and name
    sections.

    :param path: The font path.
    :return: `None` if this is no known font type, the parsed results grouped by
             section name otherwise.
    """
    if path.suffix not in KNOWN_FONT_EXTENSIONS:
        return None

    result: dict[str, None | dict[str, FONT_VALUE_TYPE]] = {"head": None, "name": None}
    with TTFont(file=path) as font:
        for key in font.keys():
            if key not in {"head", "name"}:
                continue
            value = font.get(key)
            if key == "head":
                result[key] = handle_ttfont_head(value)
            elif key == "name":
                result[key] = handle_ttfont_names(value)
    return result


def check_font(path: Path) -> str | None:
    """
    Render the relevant details for the given font.

    :param path: The font path.
    :return: `None` if no results could be determined, otherwise the rendered
             dictionary-like representation of the names section which usually
             holds the copyright data.
    """
    font_data = analyze_font(path)
    if not font_data:
        return None
    names = font_data["name"]
    if not names:
        return None
    maximum_length = max(map(len, names.keys()))
    rendered = "\n".join(
        f"{key:>{maximum_length}}: {value}" for key, value in names.items()
    )
    return rendered


def dump_to_ttx(source_path: Path, target_path: Path) -> Path:
    """
    Utility function to convert the given font to its XML representation.

    :param source_path: The font to read.
    :param target_path: The path to write to.
    :return: The target path. The same as the `target_path` if its suffix is `.ttx`,
             otherwise the `target_path` with the suffix added.
    """
    if target_path.suffix != ".ttx":
        target_path = target_path.parent / (target_path.name + ".ttx")
    ttx.ttDump(
        input=source_path,
        output=target_path,
        options=ttx.Options(rawOptions=[], numFiles=1),
    )
    return target_path
