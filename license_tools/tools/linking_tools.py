# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to binary linking.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import cast, Literal

from typecode import magic2  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
del logging


ELF_EXE = "executable"
ELF_SHARED = "shared object"
ELF_RELOC = "relocatable"
ELF_UNKNOWN = "unknown"
ELF_TYPES = [ELF_EXE, ELF_SHARED, ELF_RELOC]
ELF_TYPES_TYPE = Literal["executable", "shared object", "relocatable", "unknown"]


def _get_file_type(path: Path) -> str:
    """
    Get the file type.

    :param: The file to check.
    :return: The guessed file type.
    """
    return cast(str, magic2.file_type(path))


def is_elf(path: Path) -> bool:
    """
    Check if the given file is an ELF file.

    :param path: The file to check.
    :return: True if the file is an ELF binary, False otherwise.
    """
    file_type = _get_file_type(path).lower()
    return file_type.startswith("elf") and any(elf_type in file_type for elf_type in ELF_TYPES)


def get_elf_type(path: Path) -> ELF_TYPES_TYPE | None:
    """
    Get the ELF type of the given file.

    :param path: The file to check.
    :return: The ELF type of the given file if it is an ELF binary, None otherwise.
    """
    if not is_elf(path):
        return None
    file_type = _get_file_type(path).lower()
    for elf_type in ELF_TYPES:
        if elf_type in file_type:
            return cast(ELF_TYPES_TYPE, elf_type)
    return cast(ELF_TYPES_TYPE, ELF_UNKNOWN)


def check_shared_objects(path: Path) -> str | None:
    """
    Check which other shared objects a shared object links to.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to a shared object, `None` otherwise.
    """
    if not is_elf(path):
        return None
    if path.is_symlink():
        # Ignore symlinks as they usually are package-internal and `ldd` does not always like them.
        logger.warning(
            "Ignoring symlink %s to %s for shared object analysis.", path, path.resolve()
        )
        return None
    output = subprocess.check_output(["ldd", path], stderr=subprocess.PIPE)
    return output.decode("UTF-8")
