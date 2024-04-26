# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import datetime
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock, TestCase

import requests

from license_tools.utils import download_utils
from license_tools.utils.download_utils import ChecksumError, Download, DownloadError
from license_tools.utils.path_utils import get_files_from_directory


class DownloadTestCase(TestCase):
    def test_verify_checksum(self) -> None:
        # No checksum.
        Download(url="http://localhost", filename="dummy").verify_checksum(b"Hello World!\n")

        # Correct sha256 checksum.
        Download(
            url="http://localhost", filename="dummy", sha256="03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340"
        ).verify_checksum(b"Hello World!\n")

        # Incorrect sha256 checksum.
        with self.assertRaisesRegex(
                expected_exception=ChecksumError,
                expected_regex=r"^Checksum mismatch: Got 03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340, expected INVALID!$"
        ):
            Download(url="http://localhost", filename="dummy", sha256="INVALID").verify_checksum(b"Hello World!\n")


class GetSessionTestCase(TestCase):
    def test_get_session(self) -> None:
        session = download_utils.get_session()
        self.assertIsInstance(session, requests.Session)
        self.assertIn("https://github.com/stefan6419846/license_tools version ", session.headers["User-Agent"])


class DownloadFileTestCase(TestCase):
    def test_not_okay(self) -> None:
        session = download_utils.get_session()
        response = requests.Response()
        response.status_code = 404
        file_object = BytesIO()
        with mock.patch.object(download_utils, "get_session", return_value=session), \
                mock.patch.object(session, "get", return_value=response):
            with self.assertRaisesRegex(
                    expected_exception=DownloadError,
                    expected_regex=r"^Download not okay\? http://localhost <Response \[404\]>$"
            ):
                download_utils.download_file(
                    url="http://localhost",
                    file_object=file_object,
                )
        self.assertEqual(b"", file_object.getvalue())

    def test_valid(self) -> None:
        session = download_utils.get_session()
        response = requests.Response()
        response.status_code = 200
        response._content = b"Hello World!\n"
        file_object = BytesIO()

        with mock.patch.object(download_utils, "get_session", return_value=session), \
                mock.patch.object(session, "get", return_value=response):
            download_utils.download_file(
                url="http://localhost",
                file_object=file_object,
            )
        self.assertEqual(b"Hello World!\n", file_object.getvalue())


class DownloadFileToDirectoryTestCase(TestCase):
    def test_reuse_session(self) -> None:
        session = download_utils.get_session()
        with mock.patch.object(download_utils, "get_session") as session_mock:
            try:
                download_utils.download_file_to_directory(
                    download=Download(url="http://localhost", filename="dummy"),
                    directory=Path("/dummy"),
                    session=session
                )
            except Exception:
                pass
        session_mock.assert_not_called()

        with mock.patch.object(download_utils, "get_session") as session_mock:
            try:
                download_utils.download_file_to_directory(
                    download=Download(url="http://localhost", filename="dummy"),
                    directory=Path("/dummy"),
                )
            except Exception:
                pass
        session_mock.assert_called_once_with()

    def test_not_okay(self) -> None:
        session = download_utils.get_session()
        response = requests.Response()
        response.status_code = 404
        with mock.patch.object(session, "get", return_value=response):
            with self.assertRaisesRegex(
                    expected_exception=DownloadError,
                    expected_regex=r"^Download not okay\? http://localhost <Response \[404\]>$"
            ):
                download_utils.download_file_to_directory(
                    download=Download(url="http://localhost", filename="dummy"),
                    directory=Path("/dummy"),
                    session=session,
                )

    def test_hash_mismatch(self) -> None:
        session = download_utils.get_session()
        response = requests.Response()
        response.status_code = 200
        response._content = b"Hello World!\n"

        with mock.patch.object(session, "get", return_value=response):
            with self.assertRaisesRegex(
                    expected_exception=ChecksumError,
                    expected_regex=r"^Checksum mismatch: Got 03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340, expected INVALID!$"
            ):
                download_utils.download_file_to_directory(
                    download=Download(url="http://localhost", filename="dummy", sha256="INVALID"),
                    directory=Path("/dummy"),
                    session=session,
                )

    def test_valid(self) -> None:
        session = download_utils.get_session()
        response = requests.Response()
        response.status_code = 200
        response._content = b"Hello World!\n"

        with mock.patch.object(session, "get", return_value=response), TemporaryDirectory() as directory:
            download_utils.download_file_to_directory(
                download=Download(url="http://localhost", filename="test.txt", sha256="03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340"),
                directory=Path(directory),
                session=session,
            )
            self.assertEqual(
                b"Hello World!\n",
                Path(directory, "test.txt").read_bytes()
            )


class DownloadOneFilePerSecondTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.timestamps: list[datetime.datetime] = []
        self.downloads = [
            Download(url="http://localhost/file1", filename="file1.txt", sha256="03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340"),
            Download(url="http://localhost/file2", filename="file2.txt", sha256="03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340"),
            Download(url="http://localhost/file3", filename="file3.txt", sha256="03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340"),
        ]

        self.session = download_utils.get_session()
        self._session_patcher = mock.patch.object(download_utils, "get_session", return_value=self.session)
        self._session_patcher.start()
        self.addCleanup(self._session_patcher.stop)

    def test_error(self) -> None:
        # Set wrong hash.
        self.downloads[1].sha256 = "INVALID"

        def get(url: str, *args: Any, **kwargs: Any) -> requests.Response:
            response = requests.Response()
            response.status_code = 200
            response._content = b"Hello World!\n"
            return response

        with mock.patch.object(self.session, "get", side_effect=get), TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                    expected_exception=ChecksumError,
                    expected_regex=r"^Checksum mismatch: Got 03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340, expected INVALID!$"
            ):
                download_utils.download_one_file_per_second(downloads=self.downloads, directory=Path(directory))
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(["file1.txt"], actual)
            self.assertEqual(
                b"Hello World!\n",
                Path(directory, "file1.txt").read_bytes()
            )

    def test_delays(self) -> None:
        def get(url: str, *args: Any, **kwargs: Any) -> requests.Response:
            self.timestamps.append(datetime.datetime.now())
            response = requests.Response()
            response.status_code = 200
            response._content = b"Hello World!\n"
            return response

        with mock.patch.object(self.session, "get", side_effect=get), TemporaryDirectory() as directory:
            download_utils.download_one_file_per_second(downloads=self.downloads, directory=Path(directory))
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(["file1.txt", "file2.txt", "file3.txt"], actual)
            for name in actual:
                self.assertEqual(
                    b"Hello World!\n",
                    Path(directory, name).read_bytes(),
                    name
                )

        deltas: list[datetime.timedelta] = [y - x for x, y in zip(self.timestamps[:-1], self.timestamps[1:])]
        for delta in deltas:
            self.assertGreaterEqual(delta.total_seconds(), 1)
