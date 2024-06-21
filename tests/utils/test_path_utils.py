# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from license_tools.utils.path_utils import get_files_from_directory, DirectoryWithFixedNameContext


class GetFilesFromDirectoryTestCase(TestCase):
    def test_get_files_from_directory(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)

            directory.joinpath("module1.py").touch()
            directory.joinpath("module2.py").touch()
            directory.joinpath("submodule").mkdir(parents=True)
            directory.joinpath("submodule").joinpath("nested.py").touch()
            directory.joinpath("empty").joinpath("sub").mkdir(parents=True)
            directory.joinpath("empty").joinpath("sub").joinpath("hello.py").touch()

            result = list(get_files_from_directory(temporary_directory))
            self.assertListEqual(
                [
                    (directory / "empty" / "sub" / "hello.py", "empty/sub/hello.py"),
                    (directory / "module1.py", "module1.py"),
                    (directory / "module2.py", "module2.py"),
                    (directory / "submodule" / "nested.py", "submodule/nested.py"),
                ],
                result,
            )


class DirectoryWithFixedNameContextTestCase(TestCase):
    def test_normal(self) -> None:
        with TemporaryDirectory() as tempdir:
            with DirectoryWithFixedNameContext(Path(tempdir) / "foo") as target:
                self.assertTrue(target.is_dir())
            self.assertFalse(target.is_dir())

    def test_missing_parent(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo" / "bar"
            with self.assertRaisesRegex(
                    expected_exception=FileNotFoundError,
                    expected_regex=fr"^\[Errno 2\] No such file or directory: '{re.escape(str(target_name))}'$"
            ):
                with DirectoryWithFixedNameContext(Path(tempdir) / "foo" / "bar") as target:
                    self.assertTrue(target.is_dir())

    def test_already_existing(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            target_name.mkdir()
            with self.assertRaisesRegex(
                    expected_exception=FileExistsError,
                    expected_regex=fr"^\[Errno 17\] File exists: '{re.escape(str(target_name))}'$"
            ):
                with DirectoryWithFixedNameContext(Path(tempdir) / "foo", fallback_to_random_if_exists=False) as target:
                    self.assertTrue(target.is_dir())

        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            target_name.mkdir()
            with DirectoryWithFixedNameContext(Path(tempdir) / "foo", fallback_to_random_if_exists=True) as target:
                self.assertTrue(target.is_dir())
                self.assertNotEqual(target_name, target)

    def test_deleted_in_between(self) -> None:
        with TemporaryDirectory() as tempdir:
            target_name = Path(tempdir) / "foo"
            if sys.version_info < (3, 12):
                expected_regex = fr"^\[Errno 2\] No such file or directory: '{re.escape(str(target_name))}'$"
            else:
                expected_regex = fr"^\[Errno 2\] No such file or directory: {re.escape(repr(target_name))}$"
            with self.assertRaisesRegex(
                    expected_exception=FileNotFoundError,
                    expected_regex=expected_regex
            ):
                with DirectoryWithFixedNameContext(Path(tempdir) / "foo") as target:
                    self.assertTrue(target.is_dir())
                    target.rmdir()

    def test_do_not_delete_afterwards(self) -> None:
        with TemporaryDirectory() as tempdir:
            with DirectoryWithFixedNameContext(Path(tempdir) / "foo", delete_afterwards=False) as target:
                self.assertTrue(target.is_dir())
            self.assertTrue(target.is_dir())
