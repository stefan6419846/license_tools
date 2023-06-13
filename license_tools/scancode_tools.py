# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import datetime
import shutil
import subprocess
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

from joblib import Parallel, delayed
from scancode import api


NOT_REQUESTED = object()


@dataclass
class Author:
    author: str
    start_line: int
    end_line: int


@dataclass
class Holder:
    holder: str
    start_line: int
    end_line: int


@dataclass
class Copyright:
    copyright: str
    start_line: int
    end_line: int


@dataclass
class Copyrights:
    copyrights: list[Copyright] = dataclass_field(default_factory=list)
    holders: list[Holder] = dataclass_field(default_factory=list)
    authors: list[Author] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.copyrights = [Copyright(**x) for x in self.copyrights]
        self.holders = [Holder(**x) for x in self.holders]
        self.authors = [Author(**x) for x in self.authors]


@dataclass
class Email:
    email: str
    start_line: int
    end_line: int


@dataclass
class Emails:
    emails: list[Email] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.emails = [Email(**x) for x in self.emails]


@dataclass
class Url:
    url: str
    start_line: int
    end_line: int


@dataclass
class Urls:
    urls: list[Url] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.urls = [Url(**x) for x in self.urls]


@dataclass
class FileInfo:
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
    license_expression: str
    identifier: str
    matches: list[LicenseMatch] = dataclass_field(default_factory=list)

    def __post_init__(self):
        self.matches = [LicenseMatch(**x) for x in self.matches]


@dataclass
class Licenses:
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
    path: Path
    short_path: str
    retrieve_copyrights: bool = False
    retrieve_emails: bool = False
    retrieve_urls: bool = False
    retrieve_licenses: bool = False
    retrieve_file_info: bool = False
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


def check_shared_objects(path: Path, short_path: str) -> str:
    # https://opensource.stackexchange.com/questions/13060/linking-closed-source-with-linux-vdso-so-1
    # https://github.com/torvalds/linux/blob/master/LICENSES/exceptions/Linux-syscall-note
    # https://github.com/torvalds/linux/blob/master/COPYING
    # https://www.kernel.org/doc/html/v4.18/process/license-rules.html
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
    if retrieve_ldd_data:
        print(short_path)
        print(check_shared_objects(path=path, short_path=short_path))
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
        **kwargs
) -> Generator[FileResults, None, None]:
    with TemporaryDirectory() as working_directory:
        if archive_path.suffix == ".whl":
            # `shutil.unpack_archive` cannot handle wheel files.
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                zip_file.extractall(working_directory)
        else:
            shutil.unpack_archive(archive_path, working_directory)
        yield from run_on_directory(
            directory=working_directory,
            **kwargs
        )


def run_on_downloaded_package_file(
        package_definition: str,
        index_url: str | None = None,
        **kwargs
) -> Generator[FileResults, None, None]:
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
            **kwargs
        )


def _check_only_one_value_set(values):
    filtered = list(filter(None, values))
    return len(filtered) == 1


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
    assert _check_only_one_value_set([directory, file_path, package_definition]), 'Exactly one source is required.'

    license_counts = defaultdict(int)
    kwargs = dict(
        retrieve_copyrights=retrieve_copyrights,
        retrieve_emails=retrieve_emails,
        retrieve_file_info=retrieve_file_info,
        retrieve_urls=retrieve_urls,
        retrieve_ldd_data=retrieve_ldd_data,
        job_count=job_count,
    )

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

    print()
    print("=" * 130)
    print()
    for identifier in sorted(license_counts, key=str):
        print(f"{identifier!s:>70}", f"{license_counts[identifier]:>4d}")

    return results
