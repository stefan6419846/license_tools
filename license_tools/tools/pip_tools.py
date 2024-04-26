# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to pip.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from license_tools.utils import rendering_utils

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
    return rendering_utils.render_dictionary(
        dictionary=metadata, verbose_names_mapping=_VERBOSE_NAMES, multi_value_keys={"licensefile", "license_classifier", "requires"}
    )


def download_package(
        package_definition: str,
        download_directory: Path | str,
        index_url: str | None = None,
        prefer_sdist: bool = False
) -> None:
    """
    Download the given package and save it to the given directory.

    :param package_definition: The Python package definition to download.
    :param download_directory: The directory to download the package to.
    :param index_url: The PyPI index URL to use. Uses the default one from the `.pypirc` file if unset.
    :param prefer_sdist: Download the source distribution instead of the wheel.
    """
    command = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--no-deps",
        package_definition,
        "--dest",
        download_directory,
    ]
    if index_url:
        command += ["--index-url", index_url]
    if prefer_sdist:
        command += ["--no-binary", ":all:"]
    try:
        subprocess.run(
            command, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as exception:
        if exception.stdout:
            sys.stdout.write(exception.stdout)
        if exception.stderr:
            sys.stderr.write(exception.stderr)
        raise
