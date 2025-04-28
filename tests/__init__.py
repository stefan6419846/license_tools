# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import atexit
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.resources import files, as_file
from pathlib import Path
from tempfile import mkdtemp, NamedTemporaryFile
from typing import Generator


CACHE_DIRECTORY = Path(mkdtemp())

atexit.register(shutil.rmtree, CACHE_DIRECTORY)


@dataclass
class Download:
    url: str
    name: str
    suffix: str


def _get_or_download(download: Download) -> Path:
    path = CACHE_DIRECTORY / download.name
    if path.is_file():
        return path
    from license_tools.utils.download_utils import get_session
    session = get_session()
    path.write_bytes(session.get(url=download.url).content)
    return path


@contextmanager
def get_from_url(download: Download) -> Generator[Path]:
    with NamedTemporaryFile(suffix=download.suffix) as temp_file:
        path = Path(temp_file.name)
        source_path = _get_or_download(download)
        shutil.copy2(source_path, path)
        yield path


@contextmanager
def get_file(name: str) -> Generator[Path]:
    reference = files("tests") / "files" / name
    with as_file(reference) as path:
        yield path
