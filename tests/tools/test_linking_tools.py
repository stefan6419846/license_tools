# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock, TestCase

from license_tools.tools import linking_tools
from license_tools.tools.linking_tools import check_shared_objects
from tests import get_file
from tests.data import LICENSE_PATH, SETUP_PATH


def get_libc_path() -> Path:
    output = linking_tools.check_shared_objects(Path("/usr/bin/bc"))
    assert output is not None
    for line in output.splitlines(keepends=False):
        if "libc.so" in line:
            # 	libc.so.6 => /lib64/libc.so.6 (0x00007f281a209000)
            line = line.split("=>")[1]
            line = line.strip().split(" ")[0]
            return Path(line)
    raise ValueError("Could not determine libc.so location.")


class GetFileTypeTestCase(TestCase):
    def test_get_file_type(self) -> None:
        self.assertEqual(
            "Python script, ASCII text executable",
            linking_tools._get_file_type(SETUP_PATH)
        )
        self.assertEqual(
            "ASCII text",
            linking_tools._get_file_type(LICENSE_PATH)
        )

        with get_file("Carlito-Regular.ttf") as path:
            self.assertEqual(
                'TrueType Font data, 17 tables, 1st "GDEF", 15 names, Microsoft, language 0x409',
                linking_tools._get_file_type(path)
            )


class IsElfTestCase(TestCase):
    def test_is_elf(self) -> None:
        self.assertFalse(linking_tools.is_elf(SETUP_PATH))
        self.assertFalse(linking_tools.is_elf(LICENSE_PATH))

        with get_file("Carlito-Regular.ttf") as path:
            self.assertFalse(linking_tools.is_elf(path))

        self.assertTrue(linking_tools.is_elf(Path("/usr/bin/bc")))
        self.assertTrue(linking_tools.is_elf(get_libc_path().resolve()))  # Usually a symlink.


class GetElfTypeTestCase(TestCase):
    def test_get_elf_type(self) -> None:
        self.assertIsNone(linking_tools.get_elf_type(SETUP_PATH))
        self.assertIsNone(linking_tools.get_elf_type(LICENSE_PATH))

        with get_file("Carlito-Regular.ttf") as path:
            self.assertIsNone(linking_tools.get_elf_type(path))

        self.assertEqual(linking_tools.ELF_EXE, linking_tools.get_elf_type(Path("/usr/bin/bc")))
        self.assertEqual(linking_tools.ELF_SHARED, linking_tools.get_elf_type(get_libc_path().resolve()))  # Usually a symlink.


class CheckSharedObjectsTestCase(TestCase):
    def test_so(self) -> None:
        path = get_libc_path().resolve()
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_binary(self) -> None:
        path = Path("/usr/bin/bc")
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_python(self) -> None:
        path = Path("/tmp/libdummy.py")
        with mock.patch(
            "subprocess.check_output", return_value=b"Test output\nAnother line\n"
        ) as subprocess_mock:
            result = check_shared_objects(path)
        self.assertIsNone(result)
        subprocess_mock.assert_not_called()

    def test_symlink(self) -> None:
        with TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            target = directory.joinpath("libdummy.so.42.0.0")
            target.write_bytes(b"abc")
            source = directory.joinpath("libdummy.so")
            source.symlink_to(target=target)

            with mock.patch(
                "subprocess.check_output", return_value=b"Test output\nAnother line\n"
            ) as subprocess_mock, mock.patch.object(
                linking_tools.logger, "warning"
            ) as warning_mock, mock.patch.object(
                linking_tools, "is_elf", return_value=True
            ) as elf_mock:
                result = check_shared_objects(source)
            self.assertIsNone(result)
            subprocess_mock.assert_not_called()
            warning_mock.assert_called_once_with(
                "Ignoring symlink %s to %s for shared object analysis.", source, target
            )
            elf_mock.assert_called_once_with(source)

            with mock.patch(
                "subprocess.check_output", return_value=b"Test output\nAnother line\n"
            ) as subprocess_mock, mock.patch.object(
                linking_tools, "is_elf", return_value=True
            ) as elf_mock:
                result = check_shared_objects(source.resolve())
            self.assertEqual("Test output\nAnother line\n", result)
            subprocess_mock.assert_called_once_with(
                ["ldd", target], stderr=subprocess.PIPE
            )
            elf_mock.assert_called_once_with(source.resolve())
