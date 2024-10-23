# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Retrieve license-related data.
"""

from __future__ import annotations

import atexit
import math
import shutil
from collections import defaultdict
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import BinaryIO, cast, Generator

import scancode_config  # type: ignore[import-untyped]
from joblib import Parallel, delayed  # type: ignore[import-untyped]

from license_tools.tools import cargo_tools, font_tools, image_tools, linking_tools, pip_tools, scancode_tools
from license_tools.tools.pip_tools import download_package
from license_tools.tools.scancode_tools import FileResults, Licenses, PackageResults
from license_tools.utils import archive_utils
from license_tools.utils.download_utils import download_file
from license_tools.utils.path_utils import DirectoryWithFixedNameContext, get_files_from_directory


class RetrievalFlags:
    """
    Data retrieval flags to get shorter parameter lists.
    """

    COPYRIGHTS = 1
    EMAILS = 2
    FILE_INFO = 4
    URLS = 8
    LDD_DATA = 16
    FONT_DATA = 32
    PYTHON_METADATA = 64
    CARGO_METADATA = 128
    IMAGE_METADATA = 256

    @classmethod
    def to_int(
        cls,
        retrieve_copyrights: bool = False,
        retrieve_emails: bool = False,
        retrieve_file_info: bool = False,
        retrieve_urls: bool = False,
        retrieve_ldd_data: bool = False,
        retrieve_font_data: bool = False,
        retrieve_python_metadata: bool = False,
        retrieve_cargo_metadata: bool = False,
        retrieve_image_metadata: bool = False,
    ) -> int:
        """
        Convert the given boolean parameter values to a single integer flag value.

        :param retrieve_copyrights: Whether to retrieve copyright information.
        :param retrieve_emails: Whether to retrieve e-mails.
        :param retrieve_file_info: Whether to retrieve file-specific information.
        :param retrieve_urls: Whether to retrieve URLs.
        :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
        :param retrieve_font_data: Whether to retrieve font data.
        :param retrieve_python_metadata: Whether to retrieve Python package metadata.
        :param retrieve_cargo_metadata: Whether to retrieve Cargo metadata.
        :param retrieve_image_metadata: Whether to retrieve image metadata.
        :return: The flags derived from the given parameters.
        """
        return (
            cls.COPYRIGHTS * retrieve_copyrights
            + cls.EMAILS * retrieve_emails
            + cls.FILE_INFO * retrieve_file_info
            + cls.URLS * retrieve_urls
            + cls.LDD_DATA * retrieve_ldd_data
            + cls.FONT_DATA * retrieve_font_data
            + cls.PYTHON_METADATA * retrieve_python_metadata
            + cls.CARGO_METADATA * retrieve_cargo_metadata
            + cls.IMAGE_METADATA * retrieve_image_metadata
        )

    @classmethod
    def all(cls, as_kwargs: bool = False) -> int | dict[str, bool]:
        """
        Utility method to enable all flags.

        :param: If enabled, return kwargs instead of the integer value.
        :return: The value for all flags enabled.
        """
        value = cls.to_int(True, True, True, True, True, True, True, True, True)
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
            retrieve_font_data=cls.is_set(flags=flags, flag=cls.FONT_DATA),
            retrieve_python_metadata=cls.is_set(flags=flags, flag=cls.PYTHON_METADATA),
            retrieve_cargo_metadata=cls.is_set(flags=flags, flag=cls.CARGO_METADATA),
            retrieve_image_metadata=cls.is_set(flags=flags, flag=cls.IMAGE_METADATA),
        )


def _run_on_archive_file(path: Path, short_path: str, default_to_none: bool = False) -> FileResults | None:
    """
    Run archive-specific analysis.

    :param path: The path to run on.
    :param short_path: The short path to use for display.
    :param default_to_none: Return `None` if no results could be determined instead of an empty entry.
    :return: Explicitly declared results.
    """

    if path.suffix == ".rpm" or (path.suffixes and ".rpm" in path.suffixes):
        rpm_results = PackageResults.from_rpm(path)
        if rpm_results.declared_license_expression_spdx:
            results = _get_dummy_file_results(path=path, short_path=short_path)
            results.licenses = Licenses(
                detected_license_expression=rpm_results.declared_license_expression_spdx,
                detected_license_expression_spdx=rpm_results.declared_license_expression_spdx,
            )
            return results
    if default_to_none:
        return None
    return _get_dummy_file_results(path=path, short_path=short_path)


def _get_dummy_file_results(
        path: Path,
        short_path: str
) -> FileResults:
    """
    Get some empty dummy license results, which allows displaying the file in the
    results, but skipping the actual analysis.

    :param path: The file path to analyze.
    :param short_path: The short path to use for display.
    :return: Minimal results.
    """
    results = FileResults(path=path, short_path=short_path)
    results.licenses = Licenses()
    return results


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
    if archive_utils.can_extract(archive_path=path):
        # Archive files which can be extracted further are not being analyzed on the
        # file level. This should improve the extraction speed and avoid possible
        # memory errors as this skips running string matching on possibly large
        # archives which are binary blobs anyway and do not provide any real value.
        # Instead, just have a quick look at their headers if they provide any useful
        # values.
        return cast(
            FileResults,
            _run_on_archive_file(path=path, short_path=short_path, default_to_none=False)
        )

    retrieval_kwargs = RetrievalFlags.to_kwargs(flags=retrieval_flags)

    if path.name.startswith("Cargo.toml") and retrieval_kwargs.pop("retrieve_cargo_metadata"):
        print(short_path)
        print(cargo_tools.check_metadata(path=path) + "\n")

    # This data is not yet part of the dataclasses above, as it is a custom analysis.
    # Return early if we got a result here, as these binary files currently do not
    # provide any additional useful insights in most of the cases, but tend to be
    # larger binary blobs which just slow down the analysis.
    if retrieval_kwargs.pop("retrieve_ldd_data"):
        results = linking_tools.check_shared_objects(path=path)
        if results:
            print(short_path + "\n" + results)
            return _get_dummy_file_results(path=path, short_path=short_path)
    if retrieval_kwargs.pop("retrieve_font_data"):
        results = font_tools.check_font(path=path)
        if results:
            print(short_path + "\n" + results + "\n")
            return _get_dummy_file_results(path=path, short_path=short_path)
    if retrieval_kwargs.pop("retrieve_image_metadata"):
        results = image_tools.check_image_metadata(path=path)
        if results:
            print(short_path + "\n" + results)
            return _get_dummy_file_results(path=path, short_path=short_path)

    # Register this here as each parallel process has its own directory.
    atexit.register(scancode_tools.cleanup, scancode_config.scancode_temp_dir)

    return FileResults(
        path=path, short_path=short_path, retrieve_licenses=True,
        retrieve_copyrights=retrieval_kwargs["retrieve_copyrights"],
        retrieve_emails=retrieval_kwargs["retrieve_emails"],
        retrieve_urls=retrieval_kwargs["retrieve_urls"],
        retrieve_file_info=retrieval_kwargs["retrieve_file_info"],
    )


def run_on_directory(
    directory: str,
    job_count: int = 4,
    retrieval_flags: int = 0,
    prefix: str | None = None,
    allow_random_directory_for_archive: bool = True,
    delete_unpacked_archive_directories: bool = True,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis on the given directory.

    :param directory: The directory to analyze.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
    :param prefix: Custom prefix to use.
    :param allow_random_directory_for_archive: Allow a random directory for unpacking archives.
    :param delete_unpacked_archive_directories: Delete the directories of unpacked archives afterwards.
    :return: The requested results per file.
    """
    files = list(get_files_from_directory(directory, prefix))
    results = Parallel(n_jobs=job_count)(
        delayed(run_on_file)(
            path=path,
            short_path=short_path,
            retrieval_flags=retrieval_flags,
        )
        for path, short_path in files
    )
    yield from results

    for path, _ in files:
        if archive_utils.can_extract(path):
            name = path.name[:-len("".join(path.suffixes))]
            subdirectory = path.parent / f'{name}_{"_".join(path.suffixes).replace(".", "")}'
            with DirectoryWithFixedNameContext(
                    directory=subdirectory,
                    fallback_to_random_if_exists=allow_random_directory_for_archive,
                    delete_afterwards=delete_unpacked_archive_directories,
            ) as target_directory:
                archive_utils.extract(archive_path=path, target_directory=target_directory)
                yield from run_on_directory(
                    directory=str(target_directory),
                    job_count=job_count,
                    retrieval_flags=retrieval_flags,
                    prefix=directory,
                )


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
    archive_results = _run_on_archive_file(path=archive_path, short_path=archive_path.name, default_to_none=True)
    if archive_results is not None:
        yield archive_results

    with TemporaryDirectory() as working_directory:
        if not archive_utils.can_extract(archive_path):
            raise ValueError(f'Unsupported archive format: {archive_path}')
        archive_utils.extract(archive_path=archive_path, target_directory=Path(working_directory))

        if RetrievalFlags.is_set(flags=retrieval_flags, flag=RetrievalFlags.PYTHON_METADATA):
            print(pip_tools.check_metadata(path=working_directory) + "\n")

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
        download_file(url=download_url, file_object=cast(BinaryIO, downloaded_file))
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
    prefer_sdist: bool = False,
) -> Generator[FileResults, None, None]:
    """
    Run the analysis for the given package definition.

    :param package_definition: The package definition to get the files for.
    :param index_url: The PyPI index URL to use. Uses the default one from the `.pypirc` file if unset.
    :param job_count: The number of parallel jobs to use.
    :param retrieval_flags: Values to retrieve.
    :param prefer_sdist: Download the source distribution instead of the wheel.
    :return: The requested results.
    """
    with TemporaryDirectory() as download_directory:
        download_package(
            package_definition=package_definition,
            download_directory=download_directory,
            index_url=index_url,
            prefer_sdist=prefer_sdist,
        )
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


def run(
    directory: Path | str | None = None,
    file_path: Path | str | None = None,
    archive_path: Path | str | None = None,
    package_definition: str | None = None,
    download_url: str | None = None,
    index_url: str | None = None,
    prefer_sdist: bool = False,
    job_count: int = 4,
    retrieve_copyrights: bool = False,
    retrieve_emails: bool = False,
    retrieve_file_info: bool = False,
    retrieve_urls: bool = False,
    retrieve_ldd_data: bool = False,
    retrieve_font_data: bool = False,
    retrieve_python_metadata: bool = False,
    retrieve_cargo_metadata: bool = False,
    retrieve_image_metadata: bool = False,
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
    :param prefer_sdist: For PyPI downloads, prefer/use the source distribution over/instead of the wheel.
    :param job_count: The number of parallel jobs to use.
    :param retrieve_copyrights: Whether to retrieve copyright information.
    :param retrieve_emails: Whether to retrieve e-mails.
    :param retrieve_file_info: Whether to retrieve file-specific information.
    :param retrieve_urls: Whether to retrieve URLs.
    :param retrieve_ldd_data: Whether to retrieve linking data for shared objects.
    :param retrieve_font_data: Whether to retrieve font data.
    :param retrieve_python_metadata: Whether to retrieve Python package metadata.
    :param retrieve_cargo_metadata: Whether to retrieve Cargo metadata.
    :param retrieve_image_metadata: Whether to retrieve image metadata.
    :return: The requested results.
    """
    # Remove the temporary directory of the main thread.
    atexit.register(scancode_tools.cleanup, scancode_config.scancode_temp_dir)

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
        retrieve_font_data=retrieve_font_data,
        retrieve_python_metadata=bool(retrieve_python_metadata and package_definition),
        retrieve_cargo_metadata=retrieve_cargo_metadata,
        retrieve_image_metadata=retrieve_image_metadata,
    )

    # Run the analysis itself.
    if package_definition:
        results = list(
            run_on_downloaded_package_file(
                package_definition=package_definition,
                index_url=index_url,
                retrieval_flags=retrieval_flags,
                job_count=job_count,
                prefer_sdist=prefer_sdist,
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
        if result.licenses is None:
            continue
        licenses = result.licenses
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
        print(
            f"{identifier!s:>70}", f"{license_counts[identifier]:>{count_length + 1}d}"
        )

    return results


atexit.register(scancode_tools.cleanup, scancode_config.scancode_temp_dir)
