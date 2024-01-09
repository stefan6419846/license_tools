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

import rpmfile  # type: ignore[import-untyped]


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
    target_path = Path(target_directory)
    target_path_str = str(target_path)

    # See `rpmfile.cli` for the `extract` option.
    # This is a pathlib-based approach of the original implementation.
    #
    # Upstream code:
    # https://github.com/srossross/rpmfile/blob/c0498cd5173afb6fb0af9ed5c7d61335b7c9af0e/rpmfile/cli.py
    #
    # Original copyright:
    #
    # -------------------------------------------------------------------------
    #
    # Copyright (c) 2015 Sean Ross-Ross
    #
    # MIT License
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in all
    # copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.
    #
    # -------------------------------------------------------------------------
    #
    # The changed version can be used under either the MIT or the Apache-2.0 license,
    # depending on your preferences.
    with rpmfile.open(archive_path) as rpm_file:
        for rpm_info in rpm_file.getmembers():
            with rpm_file.extractfile(rpm_info.name) as file_object:
                directories = rpm_info.name.split("/")
                filename = directories.pop()
                if directories:
                    directories_path = target_path.joinpath(*directories).resolve()
                    if not str(directories_path).startswith(target_path_str):
                        raise ValueError(f"Attempted path traversal: {directories_path}")
                    if not directories_path.is_dir():
                        directories_path.mkdir(parents=True)
                else:
                    directories_path = target_path.resolve()
                target_file = directories_path / filename
                if not str(target_file).startswith(target_path_str):
                    raise ValueError(f"Attempted path traversal: {target_file}")
                target_file.write_bytes(file_object.read())


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
