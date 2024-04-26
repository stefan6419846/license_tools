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
from typing import BinaryIO

import requests

from license_tools.constants import VERSION


logger = logging.getLogger(__name__)
del logging


USER_AGENT = f"https://github.com/stefan6419846/license_tools version {VERSION}"


class ChecksumError(ValueError):
    """
    Error indicating a wrong checksum.
    """

    pass


@dataclass
class Download:
    """
    Configuration for one file download.
    """

    url: str
    """
    The download URL.
    """

    filename: str
    """
    The target filename.
    """

    sha256: str | None = None
    """
    The expected SHA256 checksum.
    """

    def verify_checksum(self, data: bytes) -> None:
        """
        Check if the checksum of the given data matches the expected one.

        Raises :class:`~ChecksumError` if something is wrong.

        :param data: The data to check.
        """
        if self.sha256 is not None:
            digest = hashlib.sha256(data).hexdigest()
            expected = self.sha256
        else:
            return
        if digest != expected:
            raise ChecksumError(f'Checksum mismatch: Got {digest}, expected {expected}!')


class DownloadError(ValueError):
    """
    Error indicating some (generic) download failure.
    """

    pass


def get_session() -> requests.Session:
    """
    Get an identifiable session.

    :return: The session which identifies us against the server.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def download_file(url: str, file_object: BinaryIO) -> None:
    """
    Download the given file to the given file object.

    :param url: The download URL to use.
    :param file_object: The binary file to download to. Reset after writing.
    """
    session = get_session()
    response = session.get(url)
    if not response.ok:
        raise DownloadError(f"Download not okay? {url} {response}")
    file_object.write(response.content)
    file_object.seek(0)


def download_file_to_directory(download: Download, directory: Path, session: requests.Session | None = None) -> None:
    """
    Download the given file to the given directory.

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
        download_file_to_directory(download=download, directory=directory, session=session)
        time.sleep(1)
