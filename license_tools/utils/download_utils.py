# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Download handling.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from license_tools.constants import VERSION


logger = logging.getLogger(__name__)
del logging


USER_AGENT = f"https://github.com/stefan6419846/license_tools version {VERSION}"


class ChecksumError(ValueError):
    pass


@dataclass
class Download:
    url: str
    filename: str
    sha256: str | None = None

    def verify_checksum(self, data: bytes) -> None:
        """
        Check if the checksum of the given data matches the expected one.
        """
        if self.sha256 is not None:
            digest = hashlib.sha256(data).hexdigest()
            expected = self.sha256
        else:
            return
        if digest != expected:
            raise ChecksumError(f'Checksum mismatch: Got {digest}, expected {expected}!')


class DownloadError(ValueError):
    pass


def get_session() -> requests.Session:
    """
    Get an identifiable session.

    :return: The session which identifies us against the server.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def download_file(download: Download, directory: Path, session: requests.Session | None = None) -> None:
    """
    Download the given file.

    :param download: Download to perform.
    :param directory: Directory to download to.
    :param session: Session to use.
    """
    if session is None:
        session = get_session()
    target_path = directory / download.filename
    logger.info("Downloading %s to %s ...", download.url, target_path)
    response = session.get(download.url)
    if not response.ok:
        raise DownloadError(f"Download not okay? {download.url} {response}")
    download.verify_checksum(response.content)
    target_path.write_bytes(response.content)


def download_one_file_per_second(downloads: list[Download], directory: Path) -> None:
    """
    Download the given files with not more than one request per second. This conforms to
    https://crates.io/data-access#api accordingly.

    :param downloads: List of downloads to perform.
    :param directory: Directory to download to.
    """
    session = get_session()
    for download in downloads:
        download_file(download=download, directory=directory, session=session)
        time.sleep(1)