# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Generator, Type


def get_files_from_directory(
    directory: str | Path,
    prefix: str | None = None,
) -> Generator[tuple[Path, str], None, None]:
    """
    Get the files from the given directory, recursively.

    :param directory: The directory to walk through.
    :param prefix: Custom prefix to use.
    :return: For each file, the complete Path object as well as the path string
             relative to the given directory.
    """
    directory_string = str(directory) if prefix is None else prefix
    common_prefix_length = len(directory_string) + int(
        not directory_string.endswith("/")
    )

    for path in sorted(Path(directory).rglob("*"), key=str):
        if path.is_dir():
            continue
        short_path = str(path)[common_prefix_length:]
        yield path, short_path


class DirectoryWithFixedNameContext:
    """
    Create the directory with the given name. Similar to `tempfile.TemporaryDirectory`, but with a fixed name.
    """

    def __init__(
            self,
            directory: str | Path,
            fallback_to_random_if_exists: bool = True,
            delete_afterwards: bool = True,
    ) -> None:
        """
        :param directory: The target directory to create temporarily.
        :param fallback_to_random_if_exists: Specify whether to fail if the target directory
                                             already exists or whether to fall back to a
                                             random directory with the same parent in this case.
        :param delete_afterwards: Specify whether to delete the directory on exit.
        """
        self.directory = Path(directory)
        self._consider_fallback = fallback_to_random_if_exists
        self._delete_afterwards = delete_afterwards

    def __enter__(self) -> Path:
        if self.directory.exists():
            if not self._consider_fallback:
                # Let `pathlib` handle the error reporting which contains more details.
                self.directory.mkdir(parents=False, exist_ok=False)
            else:
                self.directory = Path(mkdtemp(dir=self.directory.parent))
        else:
            self.directory.mkdir(parents=False, exist_ok=False)
        return self.directory

    def __exit__(self, type_: Type[BaseException] | None, value: BaseException | None, traceback: Any | None) -> bool | None:
        if self._delete_afterwards:
            shutil.rmtree(self.directory)

        if type_:
            # Error.
            return None
        return True
