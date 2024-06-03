# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock, TestCase

from license_tools.tools import pip_tools
from license_tools.utils import archive_utils
from license_tools.utils.path_utils import get_files_from_directory
from tests import get_from_url
from tests.data import JWCRYPTO__1_5_4__TAR_GZ, PYPDF__3_17_4__WHEEL


class AnalyzeMetadataTestCase(TestCase):
    def test_valid(self) -> None:
        with get_from_url(PYPDF__3_17_4__WHEEL) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils.extract(
                archive_path=path, target_directory=directory
            )

            result1 = asdict(pip_tools.analyze_metadata(directory / "pypdf-3.17.4.dist-info"))
            result1.pop("distribution")
            result2 = asdict(pip_tools.analyze_metadata(directory))
            result2.pop("distribution")
            self.assertEqual(result1, result2)

    def test_invalid(self) -> None:
        with TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            directory.joinpath("other").mkdir()
            with self.assertRaises(StopIteration):
                pip_tools.analyze_metadata(directory)


class CheckMetadataTestCase(TestCase):
    def test_check_metadata__dist_info(self) -> None:
        with get_from_url(PYPDF__3_17_4__WHEEL) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils.extract(
                archive_path=path, target_directory=directory
            )
            result = pip_tools.check_metadata(directory)
            self.assertEqual(f"""
               Name: pypdf
            Version: 3.17.4
      License files: {tempdir}/pypdf-3.17.4.dist-info/LICENSE
             Author: Mathieu Fenniak <biziqe@mathieu.fenniak.net>
         Maintainer: Martin Thoma <info@martin-thoma.de>
            License: UNKNOWN
License classifiers: BSD License
            Summary: A pure-python PDF library capable of splitting, merging, cropping, and transforming PDF files
           Homepage: https://github.com/py-pdf/pypdf
       Requirements:
                      * Pillow>=8.0.0 ; extra == "full"
                      * Pillow>=8.0.0 ; extra == "image"
                      * PyCryptodome ; extra == "crypto" and ( python_version == '3.6')
                      * PyCryptodome ; extra == "full" and ( python_version == '3.6')
                      * black ; extra == "dev"
                      * cryptography ; extra == "crypto" and ( python_version >= '3.7')
                      * cryptography ; extra == "full" and ( python_version >= '3.7')
                      * dataclasses; python_version < '3.7'
                      * flit ; extra == "dev"
                      * myst_parser ; extra == "docs"
                      * pip-tools ; extra == "dev"
                      * pre-commit<2.18.0 ; extra == "dev"
                      * pytest-cov ; extra == "dev"
                      * pytest-socket ; extra == "dev"
                      * pytest-timeout ; extra == "dev"
                      * pytest-xdist ; extra == "dev"
                      * sphinx ; extra == "docs"
                      * sphinx_rtd_theme ; extra == "docs"
                      * typing_extensions >= 3.7.4.3; python_version < '3.10'
                      * wheel ; extra == "dev"
"""[1:-1], result)

    def test_check_metadata__egg_info(self) -> None:
        with get_from_url(JWCRYPTO__1_5_4__TAR_GZ) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils.extract(
                archive_path=path, target_directory=directory
            )
            result = pip_tools.check_metadata(directory)
            self.assertEqual(f"""
               Name: jwcrypto
            Version: 1.5.4
      License files: {tempdir}/jwcrypto-1.5.4/LICENSE
             Author: UNKNOWN
         Maintainer: JWCrypto Project Contributors
            License: LGPLv3+
License classifiers:
            Summary: Implementation of JOSE Web standards
           Homepage: https://github.com/latchset/jwcrypto
       Requirements:
                      * cryptography>=3.4
                      * typing_extensions>=4.5.0
"""[1:-1], result)


class DownloadPackageTestCase(TestCase):
    def test_valid_package_name(self) -> None:
        stderr = StringIO()

        with redirect_stderr(stderr), TemporaryDirectory() as directory:
            pip_tools.download_package(
                package_definition="typing_extensions==4.8.0",
                index_url="https://pypi.org/simple",
                download_directory=directory
            )
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                ["typing_extensions-4.8.0-py3-none-any.whl"],
                actual
            )

        self.assertEqual("", stderr.getvalue())

    def test_prefer_source_distribution(self) -> None:
        stderr = StringIO()

        with redirect_stderr(stderr), TemporaryDirectory() as directory:
            pip_tools.download_package(
                package_definition="typing_extensions==4.8.0",
                index_url="https://pypi.org/simple",
                download_directory=directory,
                prefer_sdist=True
            )
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                ["typing_extensions-4.8.0.tar.gz"],
                actual
            )

        self.assertEqual("", stderr.getvalue())

    def test_invalid_package_name(self) -> None:
        stdout, stderr = StringIO(), StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr), TemporaryDirectory() as directory:
            with self.assertRaises(subprocess.CalledProcessError):
                pip_tools.download_package(
                    package_definition="typing_extensions==1234567890",
                    index_url="https://pypi.org/simple",
                    download_directory=directory
                )
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [],
                actual
            )

        stderr_string = stderr.getvalue()
        self.assertEqual("", stdout.getvalue())
        self.assertIn(
            "ERROR: Could not find a version that satisfies the requirement typing_extensions==1234567890 (from versions: ",
            stderr_string,
        )
        self.assertIn(
            "\nERROR: No matching distribution found for typing_extensions==1234567890\n",
            stderr_string,
        )

    def test_index_url_handling(self) -> None:
        directories = []

        def run(
            command: list[str | Path], *args: Any, **kwargs: Any
        ) -> "subprocess.CompletedProcess[bytes]":
            _directory = command[command.index("--dest") + 1]
            directories.append(_directory)
            Path(_directory).joinpath("dummy.py").touch()
            return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"")

        with mock.patch("subprocess.run", side_effect=run) as subprocess_mock:
            with TemporaryDirectory() as directory:
                pip_tools.download_package(
                    package_definition="testing", download_directory=directory
                )
            with TemporaryDirectory() as directory:
                pip_tools.download_package(
                    package_definition="testing",
                    index_url="DUMMY",
                    download_directory=directory,
                )

            subprocess_mock.assert_has_calls(
                [
                    mock.call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            "--no-deps",
                            "testing",
                            "--dest",
                            directories[0],
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    ),
                    mock.call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            "--no-deps",
                            "testing",
                            "--dest",
                            directories[1],
                            "--index-url",
                            "DUMMY",
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    ),
                ],
                any_order=False,
            )
            self.assertEqual(
                2, subprocess_mock.call_count, subprocess_mock.call_args_list
            )
