# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to binary linking.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def check_shared_objects(path: Path) -> str | None:
    """
    Check which other shared objects a shared object links to.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to a shared object, `None` otherwise.
    """
    # TODO: Handle binary files here as well (like `/usr/bin/bc`).
    if path.suffix != ".so" and not (path.suffixes and path.suffixes[0] == ".so"):
        return None
    output = subprocess.check_output(["ldd", path], stderr=subprocess.PIPE)
    return output.decode("UTF-8")
