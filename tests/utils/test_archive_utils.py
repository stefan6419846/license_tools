# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Generator
from unittest import TestCase

import requests

from license_tools import retrieval
from license_tools.utils import archive_utils
from tests.data import (
    TYPING_EXTENSION_4_8_0__SOURCE_FILES,
    TYPING_EXTENSION_4_8_0__WHEEL_FILES,
)


@contextmanager
def download(url: str, suffix: str) -> Generator[Path, None, None]:
    with NamedTemporaryFile(suffix=suffix) as temp_file:
        path = Path(temp_file.name)
        path.write_bytes(requests.get(url).content)
        yield path


class UnpackZipFileTestCase(TestCase):
    def test_jar(self) -> None:
        url = "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar"
        with download(url, ".jar") as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils._unpack_zip_file(
                archive_path=path, target_directory=directory
            )
            actual = [x[1] for x in retrieval.get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "META-INF/MANIFEST.MF",
                    "META-INF/maven/org.json/json/pom.properties",
                    "META-INF/maven/org.json/json/pom.xml",
                    "org/json/CDL.class",
                    "org/json/Cookie.class",
                    "org/json/CookieList.class",
                    "org/json/HTTP.class",
                    "org/json/HTTPTokener.class",
                    "org/json/JSONArray.class",
                    "org/json/JSONException.class",
                    "org/json/JSONML.class",
                    "org/json/JSONMLParserConfiguration.class",
                    "org/json/JSONObject$1.class",
                    "org/json/JSONObject$Null.class",
                    "org/json/JSONObject.class",
                    "org/json/JSONPointer$Builder.class",
                    "org/json/JSONPointer.class",
                    "org/json/JSONPointerException.class",
                    "org/json/JSONPropertyIgnore.class",
                    "org/json/JSONPropertyName.class",
                    "org/json/JSONString.class",
                    "org/json/JSONStringer.class",
                    "org/json/JSONTokener.class",
                    "org/json/JSONWriter.class",
                    "org/json/ParserConfiguration.class",
                    "org/json/Property.class",
                    "org/json/XML$1$1.class",
                    "org/json/XML$1.class",
                    "org/json/XML.class",
                    "org/json/XMLParserConfiguration.class",
                    "org/json/XMLTokener.class",
                    "org/json/XMLXsiTypeConverter.class",
                ],
                actual,
            )

    def test_wheel(self) -> None:
        url = "https://files.pythonhosted.org/packages/24/21/7d397a4b7934ff4028987914ac1044d3b7d52712f30e2ac7a2ae5bc86dd0/typing_extensions-4.8.0-py3-none-any.whl"  # noqa: E501
        with download(url, ".whl") as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils._unpack_zip_file(
                archive_path=path, target_directory=directory
            )
            actual = [x[1] for x in retrieval.get_files_from_directory(directory)]
            self.assertEqual(TYPING_EXTENSION_4_8_0__WHEEL_FILES, actual)


class UnpackRpmFileTestCase(TestCase):
    def test_unpack_rpm_file(self) -> None:
        url = "https://download.opensuse.org/distribution/leap/15.6/repo/oss/x86_64/libaio1-0.3.109-1.25.x86_64.rpm"
        with download(url, ".rpm") as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils._unpack_rpm_file(
                archive_path=path, target_directory=directory
            )
            actual = [x[1] for x in retrieval.get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "lib64/libaio.so.1",
                    "lib64/libaio.so.1.0.1",
                    "usr/share/doc/packages/libaio1/COPYING",
                    "usr/share/doc/packages/libaio1/TODO",
                ],
                actual,
            )


class UnpackWithShutilTestCase(TestCase):
    def test_unpack_with_shutil(self) -> None:
        url = "https://files.pythonhosted.org/packages/1f/7a/8b94bb016069caa12fc9f587b28080ac33b4fbb8ca369b98bc0a4828543e/typing_extensions-4.8.0.tar.gz"
        with download(url, ".tar.gz") as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils._unpack_with_shutil(
                archive_path=path, target_directory=directory
            )
            actual = [x[1] for x in retrieval.get_files_from_directory(directory)]
            self.assertEqual(TYPING_EXTENSION_4_8_0__SOURCE_FILES, actual)


class GetHandlerForArchiveTestCase(TestCase):
    def test_wheel(self) -> None:
        self.assertEqual(
            archive_utils._unpack_zip_file,
            archive_utils.get_handler_for_archive(Path("/path/to/package.whl")),
        )

    def test_jar(self) -> None:
        self.assertEqual(
            archive_utils._unpack_zip_file,
            archive_utils.get_handler_for_archive(Path("/path/to/package.jar")),
        )

    def test_rpm(self) -> None:
        self.assertEqual(
            archive_utils._unpack_rpm_file,
            archive_utils.get_handler_for_archive(Path("/tmp/libdummy.src.rpm")),
        )

    def test_shutil(self) -> None:
        for extension in [".tar.gz", ".tar.bz2", ".zip"]:
            with self.subTest(extension=extension):
                self.assertEqual(
                    archive_utils._unpack_with_shutil,
                    archive_utils.get_handler_for_archive(
                        Path(f"/some/path/to/file.{extension}")
                    ),
                )

    def test_unknown(self) -> None:
        self.assertIsNone(
            archive_utils.get_handler_for_archive(Path("/home/bin/run.exe"))
        )
