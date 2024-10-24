# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Archive handling.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import cast

import extractcode  # type: ignore[import-untyped]
from extractcode import all_kinds
from extractcode.api import extract_archive as _extract_archive, extract_archives as _extract_archives  # type: ignore[import-untyped]
from extractcode.archive import should_extract as _should_extract  # type: ignore[import-untyped]

# Mitigate https://github.com/aboutcode-org/extractcode/issues/65
# This is a particularly ugly workaround and I would indeed prefer an upstream
# solution, but this would most likely be more complex and require more
# research. In most cases, this should indeed be irrelevant for CLI users,
# but library users might see strange side effects on log statements etc.
# without the fix (at least when not already using UTC as the timezone anyway).
# As far as I could test it, this does not seem to have any relevant
# downsides for license retrieval.
if os.getenv("LICENSE_TOOLS_DISABLE_TZ_WORKAROUND", "").lower() == "true":  # pragma: no cover
    extractcode.libarchive2.set_env_with_tz = lambda: None


def extract(archive_path: Path, target_directory: Path, recurse: bool = False) -> None:
    """
    Extract the given archive recursively.

    :param archive_path: The archive to unpack.
    :param target_directory: The target directory to use.
    :param recurse: Whether to use a recursive approach.
    """
    if recurse:
        targets = set()
        for event in _extract_archives(location=archive_path, all_formats=True, recurse=True):
            if event.done:
                shutil.copytree(src=Path(event.target), dst=target_directory, dirs_exist_ok=True)
                targets.add(Path(event.target))
        for target in targets:
            if target.exists():
                shutil.rmtree(target)
    else:
        for _event in _extract_archive(location=archive_path, target=target_directory):
            pass


def can_extract(archive_path: Path) -> bool:
    """
    Check if the given archive can be extracted.

    :param archive_path: The path to check for.
    :return: The check result.
    """
    return cast(
        bool,
        _should_extract(
            location=archive_path,
            kinds=all_kinds,
        )
    )
