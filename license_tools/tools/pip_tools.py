# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to pip.
"""

from __future__ import annotations

from pathlib import Path
try:
    from importlib.metadata import Distribution, PathDistribution
except ImportError:
    # Python < 3.8
    from importlib_metadata import Distribution, PathDistribution  # type: ignore[assignment]

from piplicenses_lib import get_package_info


_VERBOSE_NAMES = {
    "name": "Name",
    "version": "Version",
    "licensefile": "License file",
    "author": "Author",
    "maintainer": "Maintainer",
    "license": "License",
    "license_classifier": "License classifier",
    "summary": "Summary",
    "home-page": "Homepage",
    "requires": "Requirements",
}


def analyze_metadata(path: Path | str) -> dict[str, str | list[str] | set[str] | Distribution]:
    """
    Analyze the Python package metadata for the given directory.

    :param path: The directory to analyze. Should either be a `.dist-info` one or the parent.
    :return: The package metadata.
    """
    path = Path(path)
    if path.suffix not in {".dist-info", ".egg-info"}:
        try:
            path = next(path.glob("*.dist-info"))
        except StopIteration:
            path = next(path.rglob("*.egg-info"))
    distribution = PathDistribution(path)
    return get_package_info(distribution)


def check_metadata(path: Path | str) -> str:
    """
    Render the relevant details for the given package.

    :param path: The package path.
    :return: The rendered dictionary-like representation of the relevant fields.
    """
    metadata = analyze_metadata(path)
    maximum_length = max(map(len, _VERBOSE_NAMES.values()))
    rendered = []
    for key, value in metadata.items():
        if key not in _VERBOSE_NAMES:
            continue
        if key in {"licensefile", "license_classifier", "requires"} and isinstance(value, (list, set)):
            if len(value) == 1:
                value = value.pop()
                rendered.append(f"{_VERBOSE_NAMES.get(key):>{maximum_length}}: {value}")
            elif not value:
                rendered.append(f"{_VERBOSE_NAMES.get(key):>{maximum_length}}:")
            else:
                value = "\n" + "\n".join(map(lambda x: " " * maximum_length + f"   * {x}", sorted(value)))
                rendered.append(f"{_VERBOSE_NAMES.get(key):>{maximum_length}}:{value}")
        else:
            rendered.append(f"{_VERBOSE_NAMES.get(key):>{maximum_length}}: {value}")
    return "\n".join(rendered)
