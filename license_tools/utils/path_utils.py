# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Type


class TemporaryDirectoryWithFixedName:
    """
    Create the temporary directory with the given name. Similar to `tempfile.TemporaryDirectory`,
    but with a fixed name.
    """

    def __init__(self, directory: str | Path, fallback_to_random_if_exists: bool = True) -> None:
        """
        :param directory: The target directory to create temporarily.
        :param fallback_to_random_if_exists: Specify whether to fail if the target directory
                                             already exists or whether to fall back to a
                                             random directory with the same parent in this case.
        """
        self.directory = Path(directory)
        self._consider_fallback = fallback_to_random_if_exists

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
        shutil.rmtree(self.directory)

        if type_:
            # Error.
            return None
        return True
