from __future__ import annotations

import datetime
import os
import subprocess
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import mkdtemp, NamedTemporaryFile, TemporaryDirectory
from typing import Any, cast, Dict, Generator, List
from unittest import mock, TestCase

import requests

from license_tools import scancode_tools
from license_tools.scancode_tools import Copyright, Copyrights, Emails, FileInfo, FileResults, Holder, Licenses, RetrievalFlags, Url, Urls
from tests.data import SETUP_PY_LICENSES, TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, TYPING_EXTENSION_4_8_0__LICENSES, TYPING_EXTENSION_4_8_0__SOURCE_FILES, \
    TYPING_EXTENSION_4_8_0__WHEEL_FILES

SETUP_PATH = Path(__file__).parent.parent / "setup.py"
LICENSE_PATH = SETUP_PATH.parent / "LICENSE.txt"


class LicensesTestCase(TestCase):
    def test_get_scores_of_detected_license_expression_spdx(self) -> None:
        result = SETUP_PY_LICENSES.get_scores_of_detected_license_expression_spdx()
        self.assertEqual([], result)

        file_results = FileResults(path=LICENSE_PATH, short_path="LICENSE.txt", retrieve_licenses=True)
        licenses = cast(Licenses, file_results.licenses)
        result = licenses.get_scores_of_detected_license_expression_spdx()
        self.assertEqual([100.0], result)


class FileResultsTestCase(TestCase):
    def assert_not_requested(self, result: FileResults, fields: list[str], invert: bool = False) -> None:
        method = self.assertNotEqual if invert else self.assertEqual
        for field in fields:
            with self.subTest(field=field):
                method(scancode_tools.NOT_REQUESTED, getattr(result, field))

    def test_full(self) -> None:
        flags = cast(Dict[str, bool], RetrievalFlags.all(as_kwargs=True))
        del flags["retrieve_ldd_data"]
        result = FileResults(path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True, **flags)
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "emails", "urls", "licenses", "file_info"], invert=True)

    def test_none(self) -> None:
        result = FileResults(path=Path("/tmp/dummy.py"), short_path="dummy.py")
        self.assertEqual(Path("/tmp/dummy.py"), result.path)
        self.assertEqual("dummy.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "emails", "urls", "licenses", "file_info"])

    def test_retrieve_copyrights(self) -> None:
        result = scancode_tools.FileResults(path=SETUP_PATH, short_path="setup.py", retrieve_copyrights=True)
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(result=result, fields=["emails", "urls", "licenses", "file_info"])
        expected = Copyrights(
            copyrights=[Copyright(copyright="Copyright (c) stefan6419846", start_line=1, end_line=1)],
            holders=[Holder(holder="stefan6419846", start_line=1, end_line=1)],
            authors=[]
        )
        self.assertEqual(expected, result.copyrights)

    def test_retrieve_emails(self) -> None:
        result = scancode_tools.FileResults(path=SETUP_PATH, short_path="setup.py", retrieve_emails=True)
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "urls", "licenses", "file_info"])
        expected = Emails(emails=[])
        self.assertEqual(expected, result.emails)

    def test_retrieve_urls(self) -> None:
        result = scancode_tools.FileResults(path=SETUP_PATH, short_path="setup.py", retrieve_urls=True)
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "emails", "licenses", "file_info"])
        expected = Urls(urls=[
            Url(url="http://www.apache.org/licenses/LICENSE-2.0", start_line=3, end_line=3),
            Url(url="https://github.com/stefan6419846/license_tools", start_line=21, end_line=21)
        ])
        self.assertEqual(expected, result.urls)

    def test_retrieve_licenses(self) -> None:
        self.maxDiff = None
        result = scancode_tools.FileResults(path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True)
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "emails", "urls", "file_info"])
        self.assertEqual(SETUP_PY_LICENSES, result.licenses)

    def test_retrieve_file_info(self) -> None:
        with NamedTemporaryFile(suffix=".py") as file_object:
            path = Path(file_object.name)
            path.write_text('print("Hello World!")\n')
            result = scancode_tools.FileResults(path=path, short_path="test.py", retrieve_file_info=True)

        self.assertEqual(path, result.path)
        self.assertEqual("test.py", result.short_path)
        self.assert_not_requested(result=result, fields=["copyrights", "emails", "urls", "licenses"])
        expected = FileInfo(
            date=datetime.date.today(), size=22,
            sha1="e343a35cf2fa04782749dab102d45129cdb0b644", md5="a97c0affb458a65d8682bf0a48f36e63",
            sha256="c63bf759e5502fc9f4ad863b883423a2d75992aeaebee6a713eb81fe3f714a4b",
            mime_type="text/plain", file_type="ASCII text", programming_language="Python",
            is_binary=False, is_text=True, is_archive=False, is_media=False, is_source=True, is_script=False
        )
        self.assertEqual(expected, result.file_info)


class RetrievalFlagsTestCase(TestCase):
    def test_to_int(self) -> None:
        self.assertEqual(0, RetrievalFlags.to_int())
        self.assertEqual(21, RetrievalFlags.to_int(True, False, True, False, True))

    def test_all(self) -> None:
        self.assertEqual(31, RetrievalFlags.all())
        self.assertDictEqual(
            dict(retrieve_copyrights=True, retrieve_emails=True, retrieve_file_info=True, retrieve_urls=True, retrieve_ldd_data=True),
            cast(Dict[str, bool], RetrievalFlags.all(as_kwargs=True))
        )

    def test_is_set(self) -> None:
        self.assertFalse(RetrievalFlags.is_set(flags=0, flag=RetrievalFlags.EMAILS))
        self.assertTrue(RetrievalFlags.is_set(flags=2, flag=RetrievalFlags.EMAILS))
        self.assertTrue(RetrievalFlags.is_set(flags=31, flag=RetrievalFlags.EMAILS))
        self.assertFalse(RetrievalFlags.is_set(flags=9, flag=RetrievalFlags.EMAILS))

    def test_to_kwargs(self) -> None:
        self.assertDictEqual(
            dict(retrieve_copyrights=False, retrieve_emails=False, retrieve_file_info=False, retrieve_urls=False, retrieve_ldd_data=False),
            RetrievalFlags.to_kwargs(0)
        )
        self.assertDictEqual(
            dict(retrieve_copyrights=True, retrieve_emails=False, retrieve_file_info=True, retrieve_urls=False, retrieve_ldd_data=True),
            RetrievalFlags.to_kwargs(21)
        )


class CheckSharedObjectsTestCase(TestCase):
    def test_so_suffix(self) -> None:
        path = Path("/tmp/libdummy.so")
        with mock.patch("subprocess.check_output", return_value=b"Test output\nAnother line\n") as subprocess_mock:
            result = scancode_tools.check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_so_suffix_with_multiple_suffixes(self) -> None:
        path = Path("/tmp/libdummy.so.42")
        with mock.patch("subprocess.check_output", return_value=b"Test output\nAnother line\n") as subprocess_mock:
            result = scancode_tools.check_shared_objects(path)
        self.assertEqual("Test output\nAnother line\n", result)
        subprocess_mock.assert_called_once_with(["ldd", path], stderr=subprocess.PIPE)

    def test_no_so(self) -> None:
        path = Path("/tmp/libdummy.py")
        with mock.patch("subprocess.check_output", return_value=b"Test output\nAnother line\n") as subprocess_mock:
            result = scancode_tools.check_shared_objects(path)
        self.assertIsNone(result)
        subprocess_mock.assert_not_called()


class RunOnFileTestCase(TestCase):
    def _run_mocked(self, flags: int, return_value: str | None = "") -> tuple[mock.Mock, mock.Mock, str]:
        stdout = StringIO()
        file_result = object()
        with mock.patch.object(scancode_tools, "FileResults", return_value=file_result) as results_mock, \
                redirect_stdout(stdout), \
                mock.patch.object(scancode_tools, "check_shared_objects", return_value=return_value) as check_mock:
            result = scancode_tools.run_on_file(path=SETUP_PATH, short_path="setup.py", retrieval_flags=flags)
            self.assertEqual(file_result, result)
        return results_mock, check_mock, stdout.getvalue()

    def test_run_on_file(self) -> None:
        # 1) LDD handling is inactive.
        results_mock, check_mock, stdout = self._run_mocked(flags=15)
        check_mock.assert_not_called()
        results_mock.assert_called_once_with(
            path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True, retrieve_copyrights=True, retrieve_emails=True,
            retrieve_file_info=True, retrieve_urls=True
        )
        self.assertEqual("", stdout)

        # 2) LDD handling is active, but has no results.
        for result in ["", None]:
            with self.subTest(result=result):
                results_mock, check_mock, stdout = self._run_mocked(flags=31, return_value=result)
                check_mock.assert_called_once_with(path=SETUP_PATH)
                results_mock.assert_called_once_with(
                    path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True, retrieve_copyrights=True, retrieve_emails=True,
                    retrieve_file_info=True, retrieve_urls=True
                )
                self.assertEqual("", stdout)

        # 3) LDD handling is active and has results.
        ldd_usr_bin_bc = """    linux-vdso.so.1 (0x00007fff30abf000)
    libreadline.so.7 => /lib64/libreadline.so.7 (0x00007fbe48c00000)
    libc.so.6 => /lib64/libc.so.6 (0x00007fbe48a09000)
    libtinfo.so.6 => /lib64/libtinfo.so.6 (0x00007fbe48600000)
    /lib64/ld-linux-x86-64.so.2 (0x00007fbe492b8000)
"""
        results_mock, check_mock, stdout = self._run_mocked(flags=31, return_value=ldd_usr_bin_bc)
        check_mock.assert_called_once_with(path=SETUP_PATH)
        results_mock.assert_called_once_with(
            path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True, retrieve_copyrights=True, retrieve_emails=True,
            retrieve_file_info=True, retrieve_urls=True
        )
        self.assertEqual("setup.py\n" + ldd_usr_bin_bc + "\n", stdout)


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

            result = list(scancode_tools.get_files_from_directory(temporary_directory))
            self.assertListEqual(
                [
                    (directory / "empty" / "sub" / "hello.py", "empty/sub/hello.py"),
                    (directory / "module1.py", "module1.py"),
                    (directory / "module2.py", "module2.py"),
                    (directory / "submodule" / "nested.py", "submodule/nested.py"),
                ],
                result
            )


class RunOnDirectoryTestCase(TestCase):
    def test_run_on_directory(self) -> None:
        file_results = [object()] * 5
        file_results_iterable = iter(file_results)
        paths = [(Path(f"/tmp/file{i}.py"), f"file{i}.py") for i in range(1, 6)]

        def run_on_file(path: Path, short_path: str, retrieval_flags: int = 0) -> Any:
            return next(file_results_iterable)

        with mock.patch.object(scancode_tools, "run_on_file", side_effect=run_on_file) as run_mock, \
                mock.patch.object(scancode_tools, "get_files_from_directory", return_value=paths) as get_mock:
            results = list(scancode_tools.run_on_directory("/tmp/dummy/directory", job_count=1, retrieval_flags=42))
        self.assertListEqual(file_results, results)
        run_mock.assert_has_calls(
            [mock.call(path=current_path, short_path=current_short_path, retrieval_flags=42) for current_path, current_short_path in paths],
            any_order=False
        )
        self.assertEqual(len(paths), run_mock.call_count, run_mock.call_args_list)
        get_mock.assert_called_once_with("/tmp/dummy/directory")


class RunOnPackageArchiveFileTestCase(TestCase):
    def _check_call(self, suffix: str, url: str, expected_files: List[str]) -> None:
        with NamedTemporaryFile(suffix=suffix) as archive_file:
            archive_path = Path(archive_file.name)
            archive_path.write_bytes(requests.get(url).content)

            directory_result = [object(), object(), object()]

            def run_on_directory(directory: Path, job_count: int, retrieval_flags: int) -> Generator[Any, None, None]:
                self.assertEqual(2, job_count)
                self.assertEqual(42, retrieval_flags)
                actual = [x[1] for x in scancode_tools.get_files_from_directory(directory)]
                self.assertListEqual(expected_files, actual)
                yield from directory_result

            with mock.patch.object(scancode_tools, "run_on_directory", side_effect=run_on_directory):
                result = list(scancode_tools.run_on_package_archive_file(archive_path=archive_path, job_count=2, retrieval_flags=42))
            self.assertEqual(directory_result, result)

    def test_wheel_file(self) -> None:
        url = "https://files.pythonhosted.org/packages/24/21/7d397a4b7934ff4028987914ac1044d3b7d52712f30e2ac7a2ae5bc86dd0/typing_extensions-4.8.0-py3-none-any.whl"  # noqa: E501
        self._check_call(suffix=".whl", url=url, expected_files=TYPING_EXTENSION_4_8_0__WHEEL_FILES)

    def test_non_wheel_file(self) -> None:
        url = "https://files.pythonhosted.org/packages/1f/7a/8b94bb016069caa12fc9f587b28080ac33b4fbb8ca369b98bc0a4828543e/typing_extensions-4.8.0.tar.gz"
        self._check_call(suffix=".tar.gz", url=url, expected_files=TYPING_EXTENSION_4_8_0__SOURCE_FILES)


class RunOnDownloadedPackageFileTestCase(TestCase):
    def test_valid_package_name(self) -> None:
        stderr = StringIO()

        archive_result = [object(), object(), object()]

        def run_on_package_archive_file(archive_path: Path, job_count: int, retrieval_flags: int) -> Generator[Any, None, None]:
            self.assertEqual(3, job_count)
            self.assertEqual(42, retrieval_flags)
            self.assertEqual(31584, len(archive_path.read_bytes()))
            yield from archive_result

        with redirect_stderr(stderr), \
                mock.patch.object(scancode_tools, "run_on_package_archive_file", side_effect=run_on_package_archive_file):
            result = list(scancode_tools.run_on_downloaded_package_file(
                package_definition="typing_extensions==4.8.0", index_url="https://pypi.org/simple", job_count=3, retrieval_flags=42
            ))
            self.assertEqual(archive_result, result)
        self.assertEqual("", stderr.getvalue())

    def test_invalid_package_name(self) -> None:
        stdout, stderr = StringIO(), StringIO()

        archive_result = [object(), object(), object()]
        with redirect_stdout(stdout), redirect_stderr(stderr), \
                mock.patch.object(scancode_tools, "run_on_package_archive_file", return_value=iter(archive_result)):
            with self.assertRaises(subprocess.CalledProcessError):
                list(scancode_tools.run_on_downloaded_package_file(
                    package_definition="typing_extensions==1234567890", index_url="https://pypi.org/simple", job_count=2, retrieval_flags=13
                ))

        stderr_string = stderr.getvalue()
        self.assertEqual("", stdout.getvalue())
        self.assertIn("ERROR: Could not find a version that satisfies the requirement typing_extensions==1234567890 (from versions: ", stderr_string)
        self.assertIn("\nERROR: No matching distribution found for typing_extensions==1234567890\n", stderr_string)

    def test_index_url_handling(self) -> None:
        directories = []

        def check_output(command: list[str | Path], *args: Any, **kwargs: Any) -> 'subprocess.CompletedProcess[bytes]':
            directory = command[command.index("--dest") + 1]
            directories.append(directory)
            Path(directory).joinpath("dummy.py").touch()
            return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"")

        with mock.patch.object(scancode_tools, "run_on_package_archive_file", return_value=[]), \
                mock.patch("subprocess.run", side_effect=check_output) as subprocess_mock:
            list(scancode_tools.run_on_downloaded_package_file(package_definition="testing", job_count=1, retrieval_flags=13))
            list(scancode_tools.run_on_downloaded_package_file(package_definition="testing", job_count=2, retrieval_flags=37, index_url="DUMMY"))

            subprocess_mock.assert_has_calls(
                [
                    mock.call(
                        [sys.executable, "-m", "pip", "download", "--no-deps", "testing", "--dest", directories[0]],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                    ),
                    mock.call(
                        [sys.executable, "-m", "pip", "download", "--no-deps", "testing", "--dest", directories[1], "--index-url", "DUMMY"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                    ),
                ],
                any_order=False
            )
            self.assertEqual(2, subprocess_mock.call_count, subprocess_mock.call_args_list)


class CheckThatExactlyOneValueIsSetTestCase(TestCase):
    def test_check_that_exactly_one_value_is_set(self) -> None:
        self.assertIs(
            True,
            scancode_tools._check_that_exactly_one_value_is_set([None, None, "test", None])
        )
        self.assertIs(
            False,
            scancode_tools._check_that_exactly_one_value_is_set([])
        )
        self.assertIs(
            False,
            scancode_tools._check_that_exactly_one_value_is_set([None, None])
        )


class CleanupTestCase(TestCase):
    def test_cleanup(self) -> None:
        directory_string = mkdtemp()
        directory = Path(directory_string)
        self.assertTrue(directory.is_dir())

        # 1) Existing directory.
        scancode_tools.cleanup(directory)
        self.assertFalse(directory.is_dir())

        # 2) Missing directory.
        scancode_tools.cleanup(directory)
        self.assertFalse(directory.is_dir())


class Stdout:
    def __init__(self) -> None:
        self.stdout = StringIO()

    def __str__(self) -> str:
        return self.stdout.getvalue()


class RunTestCase(TestCase):
    @contextmanager
    def record_stdout(self) -> Generator[Stdout, None, None]:
        result = Stdout()
        with mock.patch("shutil.get_terminal_size", return_value=os.terminal_size((100, 20))), \
                redirect_stdout(result.stdout):
            yield result

    def test_package_definition(self) -> None:
        with self.record_stdout() as stdout:
            with mock.patch.object(scancode_tools, "run_on_downloaded_package_file", return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES)) as run_mock:
                result = scancode_tools.run(package_definition="typing_extensions==4.8.0", index_url="https://example.org/simple")
        run_mock.assert_called_once_with(package_definition="typing_extensions==4.8.0", index_url="https://example.org/simple", retrieval_flags=0, job_count=4)
        self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
        self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_directory(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory)
            with self.record_stdout() as stdout:
                with mock.patch.object(scancode_tools, "run_on_directory", return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES)) as run_mock:
                    result = scancode_tools.run(directory=path, retrieve_ldd_data=True)
            run_mock.assert_called_once_with(directory=directory, retrieval_flags=16, job_count=4)
            self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
            self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_archive_path(self) -> None:
        with self.record_stdout() as stdout:
            with mock.patch.object(scancode_tools, "run_on_package_archive_file", return_value=iter(TYPING_EXTENSION_4_8_0__LICENSES)) as run_mock:
                result = scancode_tools.run(archive_path=Path("/tmp/dummy/typing_extensions-4.8.0.tar.gz"), retrieve_copyrights=True, job_count=1)
        run_mock.assert_called_once_with(archive_path=Path("/tmp/dummy/typing_extensions-4.8.0.tar.gz"), retrieval_flags=1, job_count=1)
        self.assertEqual(TYPING_EXTENSION_4_8_0__LICENSES, result)
        self.assertEqual(TYPING_EXTENSION_4_8_0__EXPECTED_OUTPUT, str(stdout))

    def test_file_path(self) -> None:
        with self.record_stdout() as stdout:
            result = scancode_tools.run(file_path=SETUP_PATH, job_count=1)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result), result)
        first_result = result[0]
        self.assertIsInstance(first_result, FileResults)
        self.assertEqual(SETUP_PY_LICENSES, first_result.licenses)
        self.assertEqual(f"""{SETUP_PATH} Apache-2.0 AND (LicenseRef-scancode-unknown-license-reference AND Apache-2.0) 

====================================================================================================

Apache-2.0 AND (LicenseRef-scancode-unknown-license-reference AND Apache-2.0)  1
""", str(stdout))  # noqa: W291
