# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Archive handling.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import cast

from extractcode import all_kinds  # type: ignore[import-untyped]
from extractcode.api import extract_archive as _extract_archive, extract_archives as _extract_archives  # type: ignore[import-untyped]
from extractcode.archive import should_extract as _should_extract  # type: ignore[import-untyped]


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
