# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to images.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import cast

from typecode import magic2  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
del logging


def _get_mime_type(path: Path) -> str:
    """
    Get the mime type.

    :param: The file to check.
    :return: The guessed mime type.
    """
    return cast(str, magic2.mime_type(path))


def is_image(path: Path) -> bool:
    """
    Check if the given file is an image file.

    :param path: The file to check.
    :return: True if the file is an image, False otherwise.
    """
    file_type = _get_mime_type(path).lower()
    return file_type.startswith("image")


def check_image_metadata(path: Path) -> str | None:
    """
    Check the metadata of the given image.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to an image file, `None` otherwise.
    """
    if not is_image(path):
        return None
    exiftool = shutil.which("exiftool")
    if not exiftool:
        raise ValueError("exiftool not found!")

    # The key names might be retrieved by using the `-json` option.
    output = subprocess.check_output(
        [
            exiftool,
            "-duplicates",
            "-groupnames",
            "-charset", "UTF-8",
            "-exclude", "File:Directory",
            "-exclude", "File:FileAccessDate",
            "-exclude", "File:FileInodeChangeDate",
            path
        ],
        stderr=subprocess.PIPE,
    )
    return output.decode("UTF-8")
