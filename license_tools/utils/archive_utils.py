# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Archive handling.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Protocol

from license_tools.tools import rpm_tools


class ArchiveHandler(Protocol):
    """
    Method interface for an archive handler.
    """

    def __call__(self, archive_path: Path, target_directory: Path | str) -> None:
        ...


def _unpack_zip_file(archive_path: Path, target_directory: Path | str) -> None:
    """
    Unpack the given ZIP file which requires custom handling.

    :param archive_path: The ZIP file to unpack.
    :param target_directory: The directory to unpack to.
    """
    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(target_directory)


def _unpack_rpm_file(archive_path: Path, target_directory: Path | str) -> None:
    """
    Unpack the given RPM file.

    :param archive_path: The RPM file to unpack.
    :param target_directory: The directory to unpack to.
    """
    return rpm_tools.extract(archive_path=archive_path, target_path=Path(target_directory))


def _unpack_with_shutil(archive_path: Path, target_directory: Path | str) -> None:
    """
    Unpack the given archive file which is supported out-of-the-box.

    :param archive_path: The archive file to unpack.
    :param target_directory: The directory to unpack to.
    """
    shutil.unpack_archive(filename=archive_path, extract_dir=target_directory)


def get_handler_for_archive(archive_path: Path) -> ArchiveHandler | None:
    """
    Get the handler for the given archive file.

    :param archive_path: The file to get the handler for.
    :return: If possible/known, the corresponding handler, otherwise None.
    """
    if archive_path.suffix in {".whl", ".jar"}:
        return _unpack_zip_file
    if archive_path.suffix == ".rpm":
        return _unpack_rpm_file
    if shutil._find_unpack_format(str(archive_path)):  # type: ignore[attr-defined]
        # TODO: Is there a cleaner API for this?
        return _unpack_with_shutil
    return None
