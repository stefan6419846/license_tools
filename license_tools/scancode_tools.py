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
import math
import shutil
import subprocess
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import cast, Generator

import requests
import scancode_config  # type: ignore[import-untyped]
from commoncode import fileutils  # type: ignore[import-untyped]
from joblib import Parallel, delayed  # type: ignore[import-untyped]
from scancode import api  # type: ignore[import-untyped]


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

    def __post_init__(self) -> None:
        self.copyrights = [Copyright(**x) if not isinstance(x, Copyright) else x for x in self.copyrights]  # type: ignore[arg-type]
        self.holders = [Holder(**x) if not isinstance(x, Holder) else x for x in self.holders]  # type: ignore[arg-type]
        self.authors = [Author(**x) if not isinstance(x, Author) else x for x in self.authors]  # type: ignore[arg-type]


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

    def __post_init__(self) -> None:
        self.emails = [Email(**x) if not isinstance(x, Email) else x for x in self.emails]  # type: ignore[arg-type]


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

    def __post_init__(self) -> None:
        self.urls = [Url(**x) if not isinstance(x, Url) else x for x in self.urls]  # type: ignore[arg-type]


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

    def __post_init__(self) -> None:
        if isinstance(self.date, str):
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
    rule_url: str | None


@dataclass
class LicenseClue(LicenseMatch):
    """
    Enriched matching information about a license.
    """

    pass


@dataclass
class LicenseDetection:
    """
    Information on a specific detected license.
    """

    license_expression: str
    identifier: str
    matches: list[LicenseMatch] = dataclass_field(default_factory=list)

    def __post_init__(self) -> None:
        self.matches = [LicenseMatch(**x) if not isinstance(x, LicenseMatch) else x for x in self.matches]  # type: ignore[arg-type]


@dataclass
class Licenses:
    """
    Information on all detected licenses.
    """

    detected_license_expression: str | None
    detected_license_expression_spdx: str | None
    percentage_of_license_text: float
    license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    license_clues: list[LicenseClue] = dataclass_field(default_factory=list)

    def __post_init__(self) -> None:
        self.license_detections = [
            LicenseDetection(**x) if not isinstance(x, LicenseDetection) else x for x in self.license_detections  # type: ignore[arg-type]
        ]
        self.license_clues = [
            LicenseClue(**x) if not isinstance(x, LicenseClue) else x for x in self.license_clues  # type: ignore[arg-type]
        ]

    def get_scores_of_detected_license_expression_spdx(self) -> list[float]:
        scores = []
        for detection in self.license_detections:
            if detection.license_expression == self.detected_license_expression:
                for match in detection.matches:
                    scores.append(match.score)
                return scores
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
    copyrights: Copyrights | object = NOT_REQUESTED
    emails: Emails | object = NOT_REQUESTED
    urls: Urls | object = NOT_REQUESTED
    licenses: Licenses | object = NOT_REQUESTED
    file_info: FileInfo | object = NOT_REQUESTED

    def __post_init__(self) -> None:
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


class RetrievalFlags:
    """
    Data retrieval flags to get shorter parameter lists.
    """

    COPYRIGHTS = 1
    EMAILS = 2
    FILE_INFO = 4
    URLS = 8
    LDD_DATA = 16

    @classmethod
    def to_int(
            cls,
            retrieve_copyrights: bool = False,
            retrieve_emails: bool = False,
            retrieve_file_info: bool = False,
            retrieve_urls: bool = False,
            retrieve_ldd_data: bool = False,
    ) -> int:
        """
        Convert the given boolean parameter values to a single integer flag value.

        :param retrieve_copyrights: Whether to retrieve copyright information.
        :param retrieve_emails: Whether to retrieve e-mails.
        :param retrieve_file_info: Whether to retrieve file-specific information.
        :param retrieve_urls: Whether to retrieve URLs.
        :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
        :return: The flags derived from the given parameters.
        """
        return (
            cls.COPYRIGHTS * retrieve_copyrights +
            cls.EMAILS * retrieve_emails +
            cls.FILE_INFO * retrieve_file_info +
            cls.URLS * retrieve_urls +
            cls.LDD_DATA * retrieve_ldd_data
        )

    @classmethod
    def all(cls, as_kwargs: bool = False) -> int | dict[str, bool]:
        """
        Utility method to enable all flags.

        :param: If enabled, return kwargs instead of the integer value.
        :return: The value for all flags enabled.
        """
        value = cls.to_int(True, True, True, True, True)
        if as_kwargs:
            return cls.to_kwargs(value)
        return value

    @classmethod
    def is_set(cls, flags: int, flag: int) -> bool:
        """
        Check if the given flag is set.

        :param flags: The flags to check inside.
        :param flag: The flag value to check for.
        :return: The check result.
        """
        return bool(flags & flag)

    @classmethod
    def to_kwargs(cls, flags: int) -> dict[str, bool]:
        """
        Convert the given flags to keyword arguments.

        :param flags: The flags to convert.
        :return: The associated keyword arguments.
        """
        return dict(
            retrieve_copyrights=cls.is_set(flags=flags, flag=cls.COPYRIGHTS),
            retrieve_emails=cls.is_set(flags=flags, flag=cls.EMAILS),
            retrieve_file_info=cls.is_set(flags=flags, flag=cls.FILE_INFO),
            retrieve_urls=cls.is_set(flags=flags, flag=cls.URLS),
            retrieve_ldd_data=cls.is_set(flags=flags, flag=cls.LDD_DATA),
        )


def check_shared_objects(path: Path) -> str | None:
    """
    Check which other shared objects a shared object links to.

    :param path: The file path to analyze.
    :return: The analysis results if the path points to a shared object, `None` otherwise.
    """
    # TODO: Handle binary files here as well (like `/usr/bin/bc`).
    if path.suffix != ".so" and not (path.suffixes and path.suffixes[0] == ".so"):
        return None
    output = subprocess.check_output(["ldd", path], stderr=subprocess.PIPE)
    return output.decode("UTF-8")


def run_on_file(
        path: Path,
        short_path: str,
        retrieval_flags: int = 0,
) -> FileResults:
    """
    Run the analysis on the given file.

    :param path: The file path to analyze.
    :param short_path: The short path to use for display.
    :param retrieval_flags: Values to retrieve.
    :return: The requested results.
    """
    retrieval_kwargs = RetrievalFlags.to_kwargs(flags=retrieval_flags)

    # This data is not yet part of the dataclasses above, as it is a custom analysis.
    if retrieval_kwargs.pop("retrieve_ldd_data"):
        results = check_shared_objects(path=path)
        if results:
            print(short_path + "\n" + results)

    # Register this here as each parallel process has its own directory.
    atexit.register(cleanup, scancode_config.scancode_temp_dir)

    return FileResults(
        path=path,
        short_path=short_path,
        retrieve_licenses=True,
        **retrieval_kwargs
    )


def get_files_from_directory(directory: str | Path) -> Generator[tuple[Path, str], None, None]:
    """
    Get the files from the given directory, recursively.

    :param directory: The directory to walk through.
    :return: For each file, the complete Path object as well as the path string
             relative to the given directory.
    """
    directory_string = str(directory)
    common_prefix_length = len(directory_string) + int(not directory_string.endswith("/"))

    for path in sorted(Path(directory).rglob("*"), key=str):
        if path.is_dir():
            continue
        distribution_path = str(path)[common_prefix_length:]
        yield path, distribution_path


def run_on_directory(
        directory: str,
        job_count: int = 4,
        retrieval_flags: int = 0,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given directory.

    :param directory: The directory to analyze.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
    :return: The requested results per file.
    """
    results = Parallel(n_jobs=job_count)(
        delayed(run_on_file)(
            path=path,
            short_path=short_path,
            retrieval_flags=retrieval_flags,
        ) for path, short_path in get_files_from_directory(directory)
    )
    yield from results


def run_on_package_archive_file(
        archive_path: Path,
        job_count: int = 4,
        retrieval_flags: int = 0,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given package archive file.

    :param archive_path: The package archive path to analyze.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
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
            retrieval_flags=retrieval_flags,
        )


def run_on_downloaded_archive_file(
        download_url: str,
        job_count: int = 4,
        retrieval_flags: int = 0,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given archive file after downloading it.

    :param download_url: The URL to download the archive from.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
    :return: The requested results.
    """
    # Retrieving the correct suffixes is a bit tricky here, so we use some guessing as well.
    # This basically uses the trailing URL part (usually the filename itself) and forwards
    # guessing the suffixes to Python itself. Due to the way the suffixes are determined,
    # we probably get some part of the (irrelevant) filename as well as the suffix (due to
    # dotted package versions for example), but this should not hurt. We just have to make
    # sure that we do not really loose important suffix information as Python will not be
    # able to unpack this archive otherwise, for example because we supply `.gz` instead
    # of `.tar.gz` only.
    suffixes = Path(download_url.rsplit("/", maxsplit=1)[1]).suffixes
    suffix = "".join(suffixes)
    with NamedTemporaryFile(suffix=suffix) as downloaded_file:
        response = requests.get(url=download_url)
        downloaded_file.write(response.content)
        downloaded_file.seek(0)
        yield from run_on_package_archive_file(
            archive_path=Path(downloaded_file.name),
            job_count=job_count,
            retrieval_flags=retrieval_flags,
        )


def run_on_downloaded_package_file(
        package_definition: str,
        index_url: str | None = None,
        job_count: int = 4,
        retrieval_flags: int = 0,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis for the given package definition.

    :param package_definition: The package definition to get the files for.
    :param index_url: The PyPI index URL to use. Uses the default one from the `.pypirc` file if unset.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
    :return: The requested results.
    """
    with TemporaryDirectory() as download_directory:
        command = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            package_definition,
            "--dest",
            download_directory,
        ]
        if index_url:
            command += ["--index-url", index_url]
        try:
            subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as exception:
            if exception.stdout:
                sys.stdout.write(exception.stdout.decode("UTF-8"))
            if exception.stderr:
                sys.stderr.write(exception.stderr.decode("UTF-8"))
            raise
        name = list(Path(download_directory).glob("*"))[0]
        yield from run_on_package_archive_file(
            archive_path=name.resolve(),
            job_count=job_count,
            retrieval_flags=retrieval_flags,
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
        archive_path: Path | str | None = None,
        package_definition: str | None = None,
        download_url: str | None = None,
        index_url: str | None = None,
        job_count: int = 4,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
) -> list[FileResults]:
    """
    Run the analysis for the given input definition.

    The `directory`, `file_path`, `archive_path` and `package_definition` parameters are mutually exclusive,
    but exactly one has to be set.

    :param directory: The directory to run on.
    :param file_path: The file to run on.
    :param archive_path: The package archive to run on.
    :param package_definition: The package definition to run for.
    :param download_url: The package URL to download and run on.
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

    assert _check_that_exactly_one_value_is_set(
        [directory, file_path, archive_path, package_definition, download_url]
    ), "Exactly one source is required."

    license_counts: dict[str | None, int] = defaultdict(int)
    retrieval_flags = RetrievalFlags.to_int(
        retrieve_copyrights=retrieve_copyrights,
        retrieve_emails=retrieve_emails,
        retrieve_file_info=retrieve_file_info,
        retrieve_urls=retrieve_urls,
        retrieve_ldd_data=retrieve_ldd_data,
    )

    # Run the analysis itself.
    if package_definition:
        results = list(
            run_on_downloaded_package_file(
                package_definition=package_definition,
                index_url=index_url,
                retrieval_flags=retrieval_flags,
                job_count=job_count,
            )
        )
    elif directory:
        results = list(
            run_on_directory(
                directory=str(directory),
                retrieval_flags=retrieval_flags,
                job_count=job_count,
            )
        )
    elif archive_path:
        results = list(
            run_on_package_archive_file(
                archive_path=Path(archive_path),
                retrieval_flags=retrieval_flags,
                job_count=job_count,
            )
        )
    elif download_url:
        results = list(
            run_on_downloaded_archive_file(
                download_url=download_url,
                retrieval_flags=retrieval_flags,
                job_count=job_count,
            )
        )
    elif file_path:
        results = [
            run_on_file(
                path=Path(file_path),
                short_path=str(file_path),
                retrieval_flags=retrieval_flags,
            )
        ]
    else:
        return []

    # Display the file-level results.
    max_path_length = max(len(result.short_path) for result in results)
    for result in results:
        if result.licenses == NOT_REQUESTED:
            continue
        licenses = cast(Licenses, result.licenses)
        scores = licenses.get_scores_of_detected_license_expression_spdx()
        print(
            f"{result.short_path:>{max_path_length}}",
            f"{licenses.detected_license_expression_spdx:>70}"
            if licenses.detected_license_expression_spdx
            else " " * 70,
            scores if scores else "",
        )
        license_counts[licenses.detected_license_expression_spdx] += 1

    # Display the license-level results.
    print()
    columns = shutil.get_terminal_size((80, 20)).columns
    print("=" * columns)
    print()
    count_length = max(math.log10(count) for count in license_counts.values())
    count_length = int(count_length) + 1
    for identifier in sorted(license_counts, key=str):
        print(f"{identifier!s:>70}", f"{license_counts[identifier]:>{count_length + 1}d}")

    return results
