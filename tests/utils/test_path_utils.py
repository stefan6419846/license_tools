# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from license_tools.utils.path_utils import TemporaryDirectoryWithFixedName


class TemporaryDirectoryWithFixedNameTestCase(TestCase):
    def test_normal(self) -> None:
        with TemporaryDirectory() as tempdir:
            with TemporaryDirectoryWithFixedName(Path(tempdir) / "foo") as target:
                self.assertTrue(target.is_dir())
            self.assertFalse(target.is_dir())

    def test_missing_parent(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo" / "bar"
            with self.assertRaisesRegex(
                    expected_exception=FileNotFoundError,
                    expected_regex=fr"^\[Errno 2\] No such file or directory: '{re.escape(str(target_name))}'$"
            ):
                with TemporaryDirectoryWithFixedName(Path(tempdir) / "foo" / "bar") as target:
                    self.assertTrue(target.is_dir())

    def test_already_existing(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            target_name.mkdir()
            with self.assertRaisesRegex(
                    expected_exception=FileExistsError,
                    expected_regex=fr"^\[Errno 17\] File exists: '{re.escape(str(target_name))}'$"
            ):
                with TemporaryDirectoryWithFixedName(Path(tempdir) / "foo", fallback_to_random_if_exists=False) as target:
                    self.assertTrue(target.is_dir())

        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            target_name.mkdir()
            with TemporaryDirectoryWithFixedName(Path(tempdir) / "foo", fallback_to_random_if_exists=True) as target:
                self.assertTrue(target.is_dir())
                self.assertNotEqual(target_name, target)

    def test_deleted_in_between(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            with self.assertRaisesRegex(
                    expected_exception=FileNotFoundError,
                    expected_regex=fr"^\[Errno 2\] No such file or directory: '{re.escape(str(target_name))}'$"
            ):
                with TemporaryDirectoryWithFixedName(Path(tempdir) / "foo") as target:
                    self.assertTrue(target.is_dir())
                    target.rmdir()
