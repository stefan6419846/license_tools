# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to translations.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from license_tools.utils.path_utils import get_mime_type

logger = logging.getLogger(__name__)
del logging


def is_compiled_gettext_file(path: Path) -> bool:
    """
    Check if the given file is a compiled gettext translation file.

    :param path: The file to check.
    :return: True if the file is a compiled gettext translation file, False otherwise.
    """
    mime_type = get_mime_type(path).lower()
    return mime_type.startswith("application/x-gettext-translation")


def check_compiled_gettext_metadata(path: Path) -> str | None:
    """
    Check the metadata of the given compiled gettext translation file.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to a compiled gettext translation file, `None` otherwise.
    """
    if not is_compiled_gettext_file(path):
        return None

    # Ideally, we would have used https://github.com/izimobil/polib here instead of doing subprocess calls,
    # but the package does not really appear to be maintained enough to consider it as a reliable backend.
    msgunfmt = shutil.which("msgunfmt")
    if not msgunfmt:
        raise ValueError("msgunfmt not found!")

    output = subprocess.check_output(
        [
            msgunfmt,
            path,
        ],
        stderr=subprocess.PIPE,
    )
    return output.decode("UTF-8")
