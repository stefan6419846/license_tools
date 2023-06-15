# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Convenience interface for the ScanCode toolkit project using some predefined
configuration and returning `dataclass` instances instead of dictionaries.
"""

from __future__ import annotations

import atexit
import datetime
import shutil
import subprocess
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import scancode_config
from commoncode import fileutils
from joblib import Parallel, delayed
from scancode import api


NOT_REQUESTED = object()


@dataclass
class Author:
    """
    Matching information about an author.
    """

    author: str
    start_line: int
    end_line: int


@dataclass
class Holder:
    """
    Matching information about a copyright holder.
    """

    holder: str
    start_line: int
    end_line: int


@dataclass
class Copyright:
    """
    Matching information about copyrights.
    """

    copyright: str
    start_line: int
    end_line: int


@dataclass
class Copyrights:
    """
    Copyright-specific results.
    """

    copyrights: list[Copyright] = dataclass_field(default_factory=list)
    holders: list[Holder] = dataclass_field(default_factory=list)
    authors: list[Author] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.copyrights = [Copyright(**x) for x in self.copyrights]
        self.holders = [Holder(**x) for x in self.holders]
        self.authors = [Author(**x) for x in self.authors]


@dataclass
class Email:
    """
    Matching information about an e-mail.
    """

    email: str
    start_line: int
    end_line: int


@dataclass
class Emails:
    """
    E-mail-specific results.
    """

    emails: list[Email] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.emails = [Email(**x) for x in self.emails]


@dataclass
class Url:
    """
    Matching information about an URL.
    """

    url: str
    start_line: int
    end_line: int


@dataclass
class Urls:
    """
    URL-specific results.
    """

    urls: list[Url] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.urls = [Url(**x) for x in self.urls]


@dataclass
class FileInfo:
    """
    File-specific results.
    """

    date: datetime.date
    size: int
    sha1: str
    md5: str
    sha256: str
    mime_type: str
    file_type: str
    programming_language: str
    is_binary: bool
    is_text: bool
    is_archive: bool
    is_media: bool
    is_source: bool
    is_script: bool

    def __post_init__(self):
        self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d").date()


@dataclass
class LicenseMatch:
    """
    Matching information about a license.
    """

    score: float
    start_line: int
    end_line: int
    matched_length: int
    match_coverage: float
    matcher: str
    license_expression: str
    rule_identifier: str
    rule_relevance: int
    rule_url: str


@dataclass
class LicenseDetection:
    """
    Information an a specific detected license.
    """

    license_expression: str
    identifier: str
    matches: list[LicenseMatch] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.matches = [LicenseMatch(**x) for x in self.matches]


@dataclass
class Licenses:
    """
    Information on all detected licenses.
    """

    detected_license_expression: str
    detected_license_expression_spdx: str
    percentage_of_license_text: float
    license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    license_clues: list[str] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.license_detections = [
            LicenseDetection(**x) for x in self.license_detections
        ]

    def get_scores_of_detected_license_expression_spdx(self):
        scores = []
        for detection in self.license_detections:
            if detection.license_expression == self.detected_license_expression:
                for match in detection.matches:
                    scores.append(match.score)
                return scores


@dataclass
class FileResults:
    """
    Container for all available file-level results.
    """

    # Reference to the analyzed file.
    path: Path
    short_path: str

    # Configuration values to determine which information to retrieve.
    retrieve_copyrights: bool = False
    retrieve_emails: bool = False
    retrieve_urls: bool = False
    retrieve_licenses: bool = False
    retrieve_file_info: bool = False

    # Analysis results.
    copyrights: Copyrights = NOT_REQUESTED
    emails: Emails = NOT_REQUESTED
    urls: Urls = NOT_REQUESTED
    licenses: Licenses = NOT_REQUESTED
    file_info: FileInfo = NOT_REQUESTED

    def __post_init__(self):
        path_str = str(self.path)
        if self.retrieve_copyrights:
            self.copyrights = Copyrights(**api.get_copyrights(path_str))
        if self.retrieve_emails:
            self.emails = Emails(**api.get_emails(path_str))
        if self.retrieve_urls:
            self.urls = Urls(**api.get_urls(path_str))
        if self.retrieve_licenses:
            self.licenses = Licenses(**api.get_licenses(path_str))
        if self.retrieve_file_info:
            self.file_info = FileInfo(**api.get_file_info(path_str))


def check_shared_objects(path: Path) -> str | None:
    """
    Check which other shared objects a shared object links to.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to a shared object, `None` otherwise.
    """
    if path.suffix != '.so' and not (path.suffixes and path.suffixes[0] == '.so'):
        return
    output = subprocess.check_output(['ldd', path], stderr=subprocess.PIPE)
    return output.decode('UTF-8')


def run_on_file(
        path: Path,
        short_path: str,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> FileResults:
    """
    Run the analysis on the given file.

    :param path: The file path to analyze.
    :param short_path: The short path to use for display.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :return: The requested results.
    """
    # This data is not yet part of the dataclasses above, as it is a custom analysis.
    if retrieve_ldd_data:
        results = check_shared_objects(path=path)
        if results:
            print(short_path + '\n' + results)

    # Register this here as each parallel process has its own directory.
    atexit.register(cleanup, scancode_config.scancode_temp_dir)

    return FileResults(
        path=path,
        short_path=short_path,
        retrieve_copyrights=retrieve_copyrights,
        retrieve_emails=retrieve_emails,
        retrieve_file_info=retrieve_file_info,
        retrieve_urls=retrieve_urls,
        retrieve_licenses=True,
    )


def run_on_directory(
        directory: str,
        job_count: int = 4,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given directory.

    :param path: The directory to analyze.
    :param job_count: The number of parallel jobs to use.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :return: The requested results per file.
    """
    common_prefix_length = len(directory) + int(not directory.endswith("/"))

    def get_paths() -> tuple[Path, str]:
        for path in sorted(Path(directory).rglob("*"), key=str):
            if path.is_dir():
                continue
            distribution_path = str(path)[common_prefix_length:]
            yield path, distribution_path

    results = Parallel(n_jobs=job_count)(
        delayed(run_on_file)(
            path,
            short_path,
            retrieve_copyrights,
            retrieve_emails,
            retrieve_file_info,
            retrieve_urls,
            retrieve_ldd_data,
        ) for path, short_path in get_paths()
    )
    yield from results


def run_on_package_archive_file(
        archive_path: Path,
        job_count: int = 4,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given package archive file.

    :param path: The package archive path to analyze.
    :param job_count: The number of parallel jobs to use.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :return: The requested results.
    """
    with TemporaryDirectory() as working_directory:
        if archive_path.suffix == ".whl":
            # `shutil.unpack_archive` cannot handle wheel files.
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                zip_file.extractall(working_directory)
        else:
            shutil.unpack_archive(archive_path, working_directory)
        yield from run_on_directory(
            directory=working_directory,
            job_count=job_count,
            retrieve_copyrights=retrieve_copyrights,
            retrieve_emails=retrieve_emails,
            retrieve_file_info=retrieve_file_info,
            retrieve_urls=retrieve_urls,
        )


def run_on_downloaded_package_file(
        package_definition: str,
        index_url: str | None = None,
        job_count: int = 4,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis for the given package definition.

    :param package_definition: The package definition to get the files for.
    :param index_url: The PyPI index URL to use. Uses the default one from the `.pypirc` file if unset.
    :param job_count: The number of parallel jobs to use.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :return: The requested results.
    """
    with TemporaryDirectory() as download_directory:
        command = [
            "pip",
            "download",
            "--no-deps",
            package_definition,
            "--dest",
            download_directory,
        ]
        if index_url:
            command += ["--index-url", index_url]
        subprocess.check_output(command, stderr=subprocess.PIPE)
        name = list(Path(download_directory).glob("*"))[0]
        yield from run_on_package_archive_file(
            archive_path=name.resolve(),
            job_count=job_count,
            retrieve_copyrights=retrieve_copyrights,
            retrieve_emails=retrieve_emails,
            retrieve_file_info=retrieve_file_info,
            retrieve_urls=retrieve_urls,
        )


def _check_that_exactly_one_value_is_set(values: list[Path | str | None]) -> bool:
    """
    Check that exactly one value does not evaluate to `False`.
    """
    filtered = list(filter(None, values))
    return len(filtered) == 1


def cleanup(directory: Path | str) -> None:
    """
    Remove the given directory.
    """
    fileutils.delete(directory)


def run(
        directory: Path | str | None = None,
        file_path: Path | str | None = None,
        package_definition: str | None = None,
        index_url: str | None = None,
        job_count: int = 4,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> FileResults:
    """
    Run the analysis for the given input definition.

    The `directory`, `file_path` and `package_definition` parameters are mutually exclusive,
    but exactly one has to be set.

    :param directory: The directory to run on.
    :param file_path: The file to run on.
    :param package_definition: The package definition to run for.
    :param index_url: The PyPI index URL to use. Uses the default one from the `.pypirc` file if unset.
    :param job_count: The number of parallel jobs to use.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :return: The requested results.
    """
    # Remove the temporary directory of the main thread.
    atexit.register(cleanup, scancode_config.scancode_temp_dir)

    assert _check_that_exactly_one_value_is_set([directory, file_path, package_definition]), 'Exactly one source is required.'

    license_counts = defaultdict(int)
    kwargs = dict(
        retrieve_copyrights=retrieve_copyrights,
        retrieve_emails=retrieve_emails,
        retrieve_file_info=retrieve_file_info,
        retrieve_urls=retrieve_urls,
        retrieve_ldd_data=retrieve_ldd_data,
        job_count=job_count,
    )

    # Run the analysis itself.
    if package_definition:
        results = list(
            run_on_downloaded_package_file(
                package_definition=package_definition,
                index_url=index_url,
                **kwargs
            )
        )
    elif directory:
        results = list(
            run_on_directory(
                directory=directory,
                **kwargs
            )
        )
    elif file_path:
        kwargs.pop('job_count')
        results = [
            run_on_file(
                path=file_path,
                short_path=file_path,
                **kwargs
            )
        ]

    # Display the file-level results.
    for result in results:
        scores = result.licenses.get_scores_of_detected_license_expression_spdx()
        print(
            f"{result.short_path:>50}",
            f"{result.licenses.detected_license_expression_spdx:>70}"
            if result.licenses.detected_license_expression_spdx
            else " " * 70,
            scores if scores else "",
        )
        license_counts[result.licenses.detected_license_expression_spdx] += 1

    # Display the license-level results.
    print()
    print("=" * 130)
    print()
    for identifier in sorted(license_counts, key=str):
        print(f"{identifier!s:>70}", f"{license_counts[identifier]:>4d}")

    return results
