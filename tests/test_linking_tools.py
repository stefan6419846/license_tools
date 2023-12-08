# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock, TestCase

from license_tools.linking_tools import check_shared_objects


class CheckSharedObjectsTestCase(TestCase):
    def test_so_suffix(self) -> None:
        path = Path("/tmp/libdummy.so")
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_so_suffix_with_multiple_suffixes(self) -> None:
        path = Path("/tmp/libdummy.so.42")
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_no_so(self) -> None:
        path = Path("/tmp/libdummy.py")
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertIsNone(result)
        subprocess_mock.assert_not_called()
