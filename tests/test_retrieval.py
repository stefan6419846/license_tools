# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import copy
import os
import re
import subprocess
import sys
import tarfile
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, cast, Dict, Generator, List, Set, Tuple  # TODO: Remove `Set` and `Tuple` after dropping Python 3.8.
from unittest import mock, TestCase

from license_tools import retrieval
from license_tools.retrieval import RetrievalFlags
from license_tools.tools.scancode_tools import FileResults, Licenses
from tests import Download, get_from_url
from tests.data import (
    LIBAIO1__0_3_109_1_25__RPM, SETUP_PATH,
    SETUP_PY_LICENSES,
    TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT,
    TYPING_EXTENSION_4_8_0__LICENSES,
    TYPING_EXTENSION_4_8_0__SOURCE_FILES,
    TYPING_EXTENSION_4_8_0__WHEEL_FILES, TYPING_EXTENSIONS__4_8_0__SDIST, TYPING_EXTENSIONS__4_8_0__WHEEL,
)


class RetrievalFlagsTestCase(TestCase):
    def test_to_int(self) -> None:
        self.assertEqual(0, RetrievalFlags.to_int())
        self.assertEqual(
            21, RetrievalFlags.to_int(True, False, True, False, True, False)
        )

    def test_all(self) -> None:
        self.assertEqual(127, RetrievalFlags.all())
        self.assertDictEqual(
            dict(
                retrieve_copyrights=True,
                retrieve_emails=True,
                retrieve_file_info=True,
                retrieve_urls=True,
                retrieve_ldd_data=True,
                retrieve_font_data=True,
                retrieve_python_metadata=True,
            ),
            cast(Dict[str, bool], RetrievalFlags.all(as_kwargs=True)),
        )

    def test_is_set(self) -> None:
        self.assertFalse(RetrievalFlags.is_set(flags=0, flag=RetrievalFlags.EMAILS))
        self.assertTrue(RetrievalFlags.is_set(flags=2, flag=RetrievalFlags.EMAILS))
        self.assertTrue(RetrievalFlags.is_set(flags=31, flag=RetrievalFlags.EMAILS))
        self.assertFalse(RetrievalFlags.is_set(flags=9, flag=RetrievalFlags.EMAILS))

    def test_to_kwargs(self) -> None:
        self.assertDictEqual(
            dict(
                retrieve_copyrights=False,
                retrieve_emails=False,
                retrieve_file_info=False,
                retrieve_urls=False,
                retrieve_ldd_data=False,
                retrieve_font_data=False,
                retrieve_python_metadata=False,
            ),
            RetrievalFlags.to_kwargs(0),
        )
        self.assertDictEqual(
            dict(
                retrieve_copyrights=True,
                retrieve_emails=False,
                retrieve_file_info=True,
                retrieve_urls=False,
                retrieve_ldd_data=True,
                retrieve_font_data=False,
                retrieve_python_metadata=False,
            ),
            RetrievalFlags.to_kwargs(21),
        )


class RunOnFileTestCase(TestCase):
    def _run_mocked(
        self,
        flags: int,
        mock_target: str,
        return_value: str | None = "",
    ) -> tuple[mock.Mock, mock.Mock, str]:
        stdout = StringIO()

        class DummyFileResult:
            licenses = None

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass

        file_result = DummyFileResult()
        with mock.patch.object(
            retrieval, "FileResults", return_value=file_result
        ) as results_mock, redirect_stdout(stdout), mock.patch(
            mock_target, return_value=return_value
        ) as check_mock:
            result = retrieval.run_on_file(
                path=SETUP_PATH, short_path="setup.py", retrieval_flags=flags
            )
            self.assertEqual(file_result, result)
        return results_mock, check_mock, stdout.getvalue()

    def test_run_on_file__ldd_handling(self) -> None:
        # 1) LDD handling is inactive.
        results_mock, check_mock, stdout = self._run_mocked(
            flags=15, mock_target="license_tools.tools.linking_tools.check_shared_objects"
        )
        check_mock.assert_not_called()
        results_mock.assert_called_once_with(
            path=SETUP_PATH,
            short_path="setup.py",
            retrieve_licenses=True,
            retrieve_copyrights=True,
            retrieve_emails=True,
            retrieve_file_info=True,
            retrieve_urls=True,
        )
        self.assertEqual("", stdout)

        # 2) LDD handling is active, but has no results.
        for result in ["", None]:
            with self.subTest(result=result):
                results_mock, check_mock, stdout = self._run_mocked(
                    flags=31,
                    return_value=result,
                    mock_target="license_tools.tools.linking_tools.check_shared_objects",
                )
                check_mock.assert_called_once_with(path=SETUP_PATH)
                results_mock.assert_called_once_with(
                    path=SETUP_PATH,
                    short_path="setup.py",
                    retrieve_licenses=True,
                    retrieve_copyrights=True,
                    retrieve_emails=True,
                    retrieve_file_info=True,
                    retrieve_urls=True,
                )
                self.assertEqual("", stdout)

        # 3) LDD handling is active and has results.
        ldd_usr_bin_bc = """    linux-vdso.so.1 (0x00007fff30abf000)
    libreadline.so.7 => /lib64/libreadline.so.7 (0x00007fbe48c00000)
    libc.so.6 => /lib64/libc.so.6 (0x00007fbe48a09000)
    libtinfo.so.6 => /lib64/libtinfo.so.6 (0x00007fbe48600000)
    /lib64/ld-linux-x86-64.so.2 (0x00007fbe492b8000)
"""
        results_mock, check_mock, stdout = self._run_mocked(
            flags=31,
            return_value=ldd_usr_bin_bc,
            mock_target="license_tools.tools.linking_tools.check_shared_objects",
        )
        check_mock.assert_called_once_with(path=SETUP_PATH)
        results_mock.assert_called_once_with(
            path=SETUP_PATH,
            short_path="setup.py",
        )
        self.assertEqual("setup.py\n" + ldd_usr_bin_bc + "\n", stdout)

    def test_run_on_file__font_handling(self) -> None:
        # 1) Font handling is inactive.
        results_mock, check_mock, stdout = self._run_mocked(
            flags=15, mock_target="license_tools.tools.font_tools.check_font"
        )
        check_mock.assert_not_called()
        results_mock.assert_called_once_with(
            path=SETUP_PATH,
            short_path="setup.py",
            retrieve_licenses=True,
            retrieve_copyrights=True,
            retrieve_emails=True,
            retrieve_file_info=True,
            retrieve_urls=True,
        )
        self.assertEqual("", stdout)

        # 2) Font handling is active, but has no results.
        for result in ["", None]:
            with self.subTest(result=result):
                results_mock, check_mock, stdout = self._run_mocked(
                    flags=63,
                    return_value=result,
                    mock_target="license_tools.tools.font_tools.check_font",
                )
                check_mock.assert_called_once_with(path=SETUP_PATH)
                results_mock.assert_called_once_with(
                    path=SETUP_PATH,
                    short_path="setup.py",
                    retrieve_licenses=True,
                    retrieve_copyrights=True,
                    retrieve_emails=True,
                    retrieve_file_info=True,
                    retrieve_urls=True,
                )
                self.assertEqual("", stdout)

        # 3) Font handling is active and has results.
        font_awesome = """             Copyright notice: Copyright (c) Font Awesome
          Font family name: Font Awesome 6 Free Solid
       Font subfamily name: Solid
    Unique font identifier: Font Awesome 6 Free Solid-6.5.1
            Full font name: Font Awesome 6 Free Solid
            Version string: Version 773.01171875 (Font Awesome version: 6.5.1)
           PostScript name: FontAwesome6Free-Solid
               Description: The web's most popular icon set and toolkit.
                URL Vendor: https://fontawesome.com
   Typographic Family name: Font Awesome 6 Free
Typographic Subfamily name: Solid
"""
        results_mock, check_mock, stdout = self._run_mocked(
            flags=63,
            return_value=font_awesome,
            mock_target="license_tools.tools.font_tools.check_font",
        )
        check_mock.assert_called_once_with(path=SETUP_PATH)
        results_mock.assert_called_once_with(
            path=SETUP_PATH,
            short_path="setup.py",
        )
        self.assertEqual("setup.py\n" + font_awesome + "\n\n", stdout)


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

            result = list(retrieval.get_files_from_directory(temporary_directory))
            self.assertListEqual(
                [
                    (directory / "empty" / "sub" / "hello.py", "empty/sub/hello.py"),
                    (directory / "module1.py", "module1.py"),
                    (directory / "module2.py", "module2.py"),
                    (directory / "submodule" / "nested.py", "submodule/nested.py"),
                ],
                result,
            )


class RunOnDirectoryTestCase(TestCase):
    def test_run_on_directory(self) -> None:
        file_results = [object()] * 5
        file_results_iterable = iter(file_results)
        paths = [(Path(f"/tmp/file{i}.py"), f"file{i}.py") for i in range(1, 6)]

        def run_on_file(path: Path, short_path: str, retrieval_flags: int = 0) -> Any:
            return next(file_results_iterable)

        with mock.patch.object(
            retrieval, "run_on_file", side_effect=run_on_file
        ) as run_mock, mock.patch.object(
            retrieval, "get_files_from_directory", return_value=paths
        ) as get_mock:
            results = list(
                retrieval.run_on_directory(
                    "/tmp/dummy/directory", job_count=1, retrieval_flags=42
                )
            )
        self.assertListEqual(file_results, results)
        run_mock.assert_has_calls(
            [
                mock.call(
                    path=current_path, short_path=current_short_path, retrieval_flags=42
                )
                for current_path, current_short_path in paths
            ],
            any_order=False,
        )
        self.assertEqual(len(paths), run_mock.call_count, run_mock.call_args_list)
        get_mock.assert_called_once_with("/tmp/dummy/directory", None)

    def test_nested_with_existing_directory(self) -> None:
        with TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            directory.joinpath("directory").mkdir()
            directory.joinpath("directory", "file.txt").write_text("MIT-0")
            directory.joinpath("nested_tar_bz2").write_text("Dummy")
            with TemporaryDirectory() as nested_directory:
                nested_path = Path(nested_directory)
                nested_path.joinpath("LICENSE").write_text("This is my license.")
                with tarfile.open(directory / "nested.tar.bz2", "w:bz2") as tar:
                    tar.add(nested_path, arcname=nested_path.name)

            def run_on_file(path: Path, short_path: str, retrieval_flags: int = 0) -> Any:
                return path

            with mock.patch.object(
                retrieval, "run_on_file", side_effect=run_on_file
            ) as run_mock:
                results = list(
                    retrieval.run_on_directory(
                        tempdir, job_count=1, retrieval_flags=42
                    )
                )

            self.assertSetEqual(
                {'directory', 'nested_tar_bz2', 'nested.tar.bz2'},
                {path.name for path in directory.glob('*')}
            )

        result_set: Set[Path] = cast(Set[Path], set(results))
        expected: List[Tuple[Path, str]] = []
        self.assertEqual(4, len(results), results)
        for name in ["directory/file.txt", "nested.tar.bz2", "nested_tar_bz2"]:
            result_set.remove(directory / name)
            expected.append((directory / name, name))
        self.assertEqual(1, len(result_set), result_set)
        remaining = result_set.pop()
        self.assertEqual(directory, remaining.parent.parent.parent)
        self.assertEqual(nested_path.name, remaining.parent.name)
        self.assertEqual("LICENSE", remaining.name)
        expected.append((remaining, "/".join(str(remaining).rsplit("/", maxsplit=3)[1:])))

        run_mock.assert_has_calls(
            [
                mock.call(
                    path=current_path, short_path=current_short_path, retrieval_flags=42
                )
                for current_path, current_short_path in expected
            ],
            any_order=False,
        )
        self.assertEqual(len(expected), run_mock.call_count, run_mock.call_args_list)

    def test_nested_without_existing_directory(self) -> None:
        with TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            directory.joinpath("directory").mkdir()
            directory.joinpath("directory", "file.txt").write_text("MIT-0")
            with TemporaryDirectory() as nested_directory:
                nested_path = Path(nested_directory)
                nested_path.joinpath("LICENSE").write_text("This is my license.")
                with tarfile.open(directory / "nested.tar.bz2", "w:bz2") as tar:
                    tar.add(nested_path, arcname=nested_path.name)

            def run_on_file(path: Path, short_path: str, retrieval_flags: int = 0) -> Any:
                return path

            with mock.patch.object(
                retrieval, "run_on_file", side_effect=run_on_file
            ) as run_mock:
                results = list(
                    retrieval.run_on_directory(
                        tempdir, job_count=1, retrieval_flags=42
                    )
                )

            self.assertSetEqual(
                {'directory', 'nested.tar.bz2'},
                {path.name for path in directory.glob('*')}
            )

        result_set: Set[Path] = cast(Set[Path], set(results))
        expected: List[Tuple[Path, str]] = []
        self.assertEqual(3, len(results), results)
        for name in ["directory/file.txt", "nested.tar.bz2"]:
            result_set.remove(directory / name)
            expected.append((directory / name, name))
        self.assertEqual(1, len(result_set), result_set)
        remaining = result_set.pop()
        self.assertEqual(directory, remaining.parent.parent.parent)
        self.assertEqual(nested_path.name, remaining.parent.name)
        self.assertEqual("LICENSE", remaining.name)
        expected.append((remaining, "/".join(str(remaining).rsplit("/", maxsplit=3)[1:])))

        run_mock.assert_has_calls(
            [
                mock.call(
                    path=current_path, short_path=current_short_path, retrieval_flags=42
                )
                for current_path, current_short_path in expected
            ],
            any_order=False,
        )
        self.assertEqual(len(expected), run_mock.call_count, run_mock.call_args_list)


class RunOnPackageArchiveFileTestCase(TestCase):
    def _check_call(self, download: Download, expected_files: List[str], expected_license: str | None = None) -> None:
        with get_from_url(download) as archive_path:
            directory_result = [object(), object(), object()]

            def run_on_directory(
                directory: Path, job_count: int, retrieval_flags: int
            ) -> Generator[Any, None, None]:
                self.assertEqual(2, job_count)
                self.assertEqual(42, retrieval_flags)
                actual = [x[1] for x in retrieval.get_files_from_directory(directory)]
                self.assertListEqual(expected_files, actual)
                yield from directory_result

            with mock.patch.object(
                retrieval, "run_on_directory", side_effect=run_on_directory
            ):
                result = list(
                    retrieval.run_on_package_archive_file(
                        archive_path=archive_path, job_count=2, retrieval_flags=42
                    )
                )

            expected = directory_result
            if expected_license:
                dummy_entry = retrieval._get_dummy_file_results(path=archive_path, short_path=archive_path.name)
                dummy_entry.licenses = Licenses(
                    detected_license_expression=expected_license,
                    detected_license_expression_spdx=expected_license,
                )
                expected.insert(0, dummy_entry)
            self.assertEqual(expected, result)

    def test_wheel_file(self) -> None:
        self._check_call(
            download=TYPING_EXTENSIONS__4_8_0__WHEEL, expected_files=TYPING_EXTENSION_4_8_0__WHEEL_FILES,
        )

    def test_non_wheel_file(self) -> None:
        self._check_call(
            download=TYPING_EXTENSIONS__4_8_0__SDIST, expected_files=TYPING_EXTENSION_4_8_0__SOURCE_FILES,
        )

    def test_rpm(self) -> None:
        self._check_call(
            download=LIBAIO1__0_3_109_1_25__RPM,
            expected_files=[
                "lib64/libaio.so.1.0.1",
                "usr/share/doc/packages/libaio1/COPYING",
                "usr/share/doc/packages/libaio1/TODO",
            ],
            expected_license="LGPL-2.1-or-later",
        )


class RunOnDownloadedArchiveFileTestCase(TestCase):
    def _check_call(self, download: Download) -> None:
        directory_result = [object(), object(), object()]

        def run_on_package_archive_file(
            archive_path: Path, job_count: int, retrieval_flags: int
        ) -> Generator[Any, None, None]:
            self.assertEqual(2, job_count)
            self.assertEqual(42, retrieval_flags)
            self.assertEqual(download.suffix, archive_path.name[-len(download.suffix):])
            yield from directory_result

        with mock.patch.object(
            retrieval,
            "run_on_package_archive_file",
            side_effect=run_on_package_archive_file,
        ):
            result = list(
                retrieval.run_on_downloaded_archive_file(
                    download_url=download.url, job_count=2, retrieval_flags=42
                )
            )
        self.assertEqual(directory_result, result)

    def test_wheel_file(self) -> None:
        self._check_call(download=TYPING_EXTENSIONS__4_8_0__WHEEL)

    def test_non_wheel_file(self) -> None:
        self._check_call(download=TYPING_EXTENSIONS__4_8_0__SDIST)


class RunOnDownloadedPackageFileTestCase(TestCase):
    def test_valid_package_name(self) -> None:
        stderr = StringIO()

        archive_result = [object(), object(), object()]

        def run_on_package_archive_file(
            archive_path: Path, job_count: int, retrieval_flags: int, retrieve_python_metadata: bool = False
        ) -> Generator[Any, None, None]:
            self.assertEqual(3, job_count)
            self.assertEqual(42, retrieval_flags)
            self.assertEqual(31584, len(archive_path.read_bytes()))
            yield from archive_result

        with redirect_stderr(stderr), mock.patch.object(
            retrieval,
            "run_on_package_archive_file",
            side_effect=run_on_package_archive_file,
        ):
            result = list(
                retrieval.run_on_downloaded_package_file(
                    package_definition="typing_extensions==4.8.0",
                    index_url="https://pypi.org/simple",
                    job_count=3,
                    retrieval_flags=42,
                )
            )
            self.assertEqual(archive_result, result)
        self.assertEqual("", stderr.getvalue())

    def test_invalid_package_name(self) -> None:
        stdout, stderr = StringIO(), StringIO()

        archive_result = [object(), object(), object()]
        with redirect_stdout(stdout), redirect_stderr(stderr), mock.patch.object(
            retrieval, "run_on_package_archive_file", return_value=iter(archive_result)
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                list(
                    retrieval.run_on_downloaded_package_file(
                        package_definition="typing_extensions==1234567890",
                        index_url="https://pypi.org/simple",
                        job_count=2,
                        retrieval_flags=13,
                    )
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

        def check_output(
            command: list[str | Path], *args: Any, **kwargs: Any
        ) -> "subprocess.CompletedProcess[bytes]":
            directory = command[command.index("--dest") + 1]
            directories.append(directory)
            Path(directory).joinpath("dummy.py").touch()
            return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"")

        with mock.patch.object(
            retrieval, "run_on_package_archive_file", return_value=[]
        ), mock.patch("subprocess.run", side_effect=check_output) as subprocess_mock:
            list(
                retrieval.run_on_downloaded_package_file(
                    package_definition="testing", job_count=1, retrieval_flags=13
                )
            )
            list(
                retrieval.run_on_downloaded_package_file(
                    package_definition="testing",
                    job_count=2,
                    retrieval_flags=37,
                    index_url="DUMMY",
                )
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
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
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
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                    ),
                ],
                any_order=False,
            )
            self.assertEqual(
                2, subprocess_mock.call_count, subprocess_mock.call_args_list
            )


class CheckThatExactlyOneValueIsSetTestCase(TestCase):
    def test_check_that_exactly_one_value_is_set(self) -> None:
        self.assertIs(
            True,
            retrieval._check_that_exactly_one_value_is_set([None, None, "test", None]),
        )
        self.assertIs(False, retrieval._check_that_exactly_one_value_is_set([]))
        self.assertIs(
            False, retrieval._check_that_exactly_one_value_is_set([None, None])
        )


class Stdout:
    def __init__(self) -> None:
        self.stdout = StringIO()

    def __str__(self) -> str:
        return self.stdout.getvalue()


class RunTestCase(TestCase):
    @contextmanager
    def record_stdout(self) -> Generator[Stdout, None, None]:
        result = Stdout()
        with mock.patch(
            "shutil.get_terminal_size", return_value=os.terminal_size((100, 20))
        ), redirect_stdout(result.stdout):
            yield result

    def test_package_definition(self) -> None:
        with self.record_stdout() as stdout:
            with mock.patch.object(
                retrieval,
                "run_on_downloaded_package_file",
                return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES),
            ) as run_mock:
                result = retrieval.run(
                    package_definition="typing_extensions==4.8.0",
                    index_url="https://example.org/simple",
                )
        run_mock.assert_called_once_with(
            package_definition="typing_extensions==4.8.0",
            index_url="https://example.org/simple",
            retrieval_flags=0,
            job_count=4,
        )
        self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
        self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_package_definition__with_metadata(self) -> None:
        self.maxDiff = None
        with self.record_stdout() as stdout:
            result = retrieval.run(
                package_definition="typing_extensions==4.8.0",
                index_url="https://pypi.org/simple",
                retrieve_python_metadata=True,
            )

        expected_result = copy.deepcopy(TYPING_EXTENSION_4_8_0__LICENSES)
        for entry in expected_result:
            entry.path = Path("dummy")
            entry.retrieve_licenses = True
        for entry in result:
            entry.path = Path("dummy")
        self.assertEqual(expected_result, result)

        expected_output = """              Name: typing_extensions
           Version: 4.8.0
      License file: /tmp/dummy/typing_extensions-4.8.0.dist-info/LICENSE
      Requirements:
          Homepage: https://github.com/python/typing_extensions
            Author: "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee" <levkivskyi@gmail.com>
        Maintainer: UNKNOWN
           License: UNKNOWN
           Summary: Backported and Experimental Type Hints for Python 3.8+
License classifier: Python Software Foundation License

""" + TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT
        self.assertEqual(expected_output, re.sub(pattern=r"/tmp/tmp[^/]+", repl="/tmp/dummy", string=str(stdout)))

    def test_directory(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory)
            with self.record_stdout() as stdout:
                with mock.patch.object(
                    retrieval,
                    "run_on_directory",
                    return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES),
                ) as run_mock:
                    result = retrieval.run(directory=path, retrieve_ldd_data=True)
            run_mock.assert_called_once_with(
                directory=directory, retrieval_flags=16, job_count=4
            )
            self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
            self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_archive_path(self) -> None:
        with self.record_stdout() as stdout:
            with mock.patch.object(
                retrieval,
                "run_on_package_archive_file",
                return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES),
            ) as run_mock:
                result = retrieval.run(
                    archive_path=Path("/tmp/dummy/typing_extensions-4.8.0.tar.gz"),
                    retrieve_copyrights=True,
                    job_count=1,
                )
        run_mock.assert_called_once_with(
            archive_path=Path("/tmp/dummy/typing_extensions-4.8.0.tar.gz"),
            retrieval_flags=1,
            job_count=1,
        )
        self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
        self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_download_url(self) -> None:
        with self.record_stdout() as stdout:
            with mock.patch.object(
                retrieval,
                "run_on_downloaded_archive_file",
                return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES),
            ) as run_mock:
                result = retrieval.run(
                    download_url="https://example.org/archive.tar.gz",
                    retrieve_copyrights=True,
                    job_count=1,
                )
        run_mock.assert_called_once_with(
            download_url="https://example.org/archive.tar.gz",
            retrieval_flags=1,
            job_count=1,
        )
        self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
        self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_file_path(self) -> None:
        with self.record_stdout() as stdout:
            result = retrieval.run(file_path=SETUP_PATH, job_count=1)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result), result)
        first_result = result[0]
        self.assertIsInstance(first_result, FileResults)
        self.assertEqual(SETUP_PY_LICENSES, first_result.licenses)
        self.assertEqual(
            f"""{SETUP_PATH} Apache-2.0 AND (LicenseRef-scancode-unknown-license-reference AND Apache-2.0) 

====================================================================================================

Apache-2.0 AND (LicenseRef-scancode-unknown-license-reference AND Apache-2.0)  1
""",  # noqa: W291
            str(stdout),
        )

    def test_nested_archive(self) -> None:
        # url = "https://download.opensuse.org/source/distribution/leap/15.6/repo/oss/src/libaio-0.3.109-1.25.src.rpm"  # Takes too long.
        with TemporaryDirectory() as archive_directory, NamedTemporaryFile(suffix=".tar.gz") as archive_file:
            archive_directory_path = Path(archive_directory)
            archive_directory_path.joinpath("directory1", "directory2").mkdir(parents=True)
            archive_directory_path.joinpath("directory1", "directory2", "file.txt").write_text("MIT-0")
            archive_directory_path.joinpath("directory1", "directory2", "file2.txt").write_text("Apache-2.0")
            with TemporaryDirectory() as nested_directory:
                nested_path = Path(nested_directory)
                nested_path.joinpath("subdirectory").mkdir()
                nested_path.joinpath("subdirectory", "README").write_text("CC-BY-2.0")
                nested_path.joinpath("LICENSE").write_text("This is my license.")
                with tarfile.open(archive_directory_path / "nested.tar.bz2", "w:bz2") as tar:
                    tar.add(nested_path, arcname=nested_path.name)

            archive_path = Path(archive_file.name)
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(archive_directory_path, arcname=archive_directory_path.name)

            with self.record_stdout() as stdout:
                result = retrieval.run(archive_path=archive_path, job_count=1)

        self.assertIsInstance(result, list)
        self.assertEqual(5, len(result), result)
        self.assertEqual(
            f"""                {archive_directory_path.name}/directory1/directory2/file.txt                                                                        
               {archive_directory_path.name}/directory1/directory2/file2.txt                                                             Apache-2.0 [100.0]
                                {archive_directory_path.name}/nested.tar.bz2                                                                        
            {archive_directory_path.name}/nested_tar_bz2/{nested_path.name}/LICENSE                                                                        
{archive_directory_path.name}/nested_tar_bz2/{nested_path.name}/subdirectory/README                                                              CC-BY-2.0 [50.0]

====================================================================================================

                                                            Apache-2.0  1
                                                             CC-BY-2.0  1
                                                                  None  3
""",  # noqa: E501, W291
            str(stdout),
        )
