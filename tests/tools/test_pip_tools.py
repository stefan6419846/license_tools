# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from license_tools.tools import pip_tools
from license_tools.utils import archive_utils
from tests import get_from_url
from tests.data import JWCRYPTO__1_5_4__TAR_GZ, PYPDF__3_17_4__WHEEL


class AnalyzeMetadataTestCase(TestCase):
    def test_valid(self) -> None:
        with get_from_url(PYPDF__3_17_4__WHEEL) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            archive_utils.extract(
                archive_path=path, target_directory=directory
            )

            result1 = pip_tools.analyze_metadata(directory / "pypdf-3.17.4.dist-info")
            result1.pop("distribution")
            result2 = pip_tools.analyze_metadata(directory)
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
      License file: {tempdir}/pypdf-3.17.4.dist-info/LICENSE
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
          Homepage: https://github.com/py-pdf/pypdf
            Author: Mathieu Fenniak <biziqe@mathieu.fenniak.net>
        Maintainer: Martin Thoma <info@martin-thoma.de>
           License: UNKNOWN
           Summary: A pure-python PDF library capable of splitting, merging, cropping, and transforming PDF files
License classifier: BSD License
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
      License file: {tempdir}/jwcrypto-1.5.4/LICENSE
      Requirements:
                     * cryptography>=3.4
                     * typing_extensions>=4.5.0
          Homepage: https://github.com/latchset/jwcrypto
            Author: UNKNOWN
        Maintainer: JWCrypto Project Contributors
           License: LGPLv3+
           Summary: Implementation of JOSE Web standards
License classifier:
"""[1:-1], result)
