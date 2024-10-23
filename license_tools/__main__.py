# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import argparse
import logging
from typing import cast


def log_level_type(value: str | int) -> int:
    """
    Verify and convert a log level to an integer value.

    :param value: The value to validate/convert.
    :return: The corresponding integer value.
    """
    if isinstance(value, int):
        return value
    return cast(int, getattr(logging, value.upper()))


def configure_logging(level: int) -> None:
    """
    Configure the logging for the application.

    :param level: The log level to use.
    """
    logging.basicConfig(level=level)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run selected license tools. Will determine all licenses from the given source by default.",
    )

    source_group = parser.add_argument_group("Artifact source")
    source_group = source_group.add_mutually_exclusive_group(required=False)
    source_group.add_argument(
        "--directory", action="store", type=str, help="Directory to work on."
    )
    source_group.add_argument(
        "--file", action="store", type=str, help="File to work on."
    )
    source_group.add_argument(
        "--archive", action="store", type=str, help="Archive file to work on."
    )
    source_group.add_argument(
        "--package",
        action="store",
        type=str,
        help="Python package specification to use.",
    )
    source_group.add_argument(
        "--url", action="store", type=str, help="Download URL to use."
    )

    parser.add_argument(
        "--index-url",
        action="store",
        type=str,
        required=False,
        default="",
        help="PyPI index URL to use.",
    )
    parser.add_argument(
        "--prefer-sdist",
        action="store_true",
        default=False,
        required=False,
        help="Prefer/download the sdist over wheels on PyPI.",
    )

    parser.add_argument(
        "--jobs",
        action="store",
        type=int,
        required=False,
        default=4,
        help="Parallel jobs to use.",
    )

    parser.add_argument(
        "--retrieve-copyrights",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve copyrights.",
    )
    parser.add_argument(
        "--retrieve-emails",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve e-mails.",
    )
    parser.add_argument(
        "--retrieve-file-info",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve file information.",
    )
    parser.add_argument(
        "--retrieve-urls",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve URLs.",
    )
    parser.add_argument(
        "--retrieve-ldd-data",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve shared object linking data.",
    )
    parser.add_argument(
        "--retrieve-font-data",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve font metadata.",
    )
    parser.add_argument(
        "--retrieve-python-metadata",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve Python package metadata.",
    )
    parser.add_argument(
        "--retrieve-cargo-metadata",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve Cargo/Rust package metadata.",
    )
    parser.add_argument(
        "--retrieve-image-metadata",
        action="store_true",
        required=False,
        default=False,
        help="Retrieve image metadata.",
    )

    parser.add_argument(
        "--cargo-lock-download",
        action="store_true",
        required=False,
        default=False,
        help="Instead of analyzing the files, download the packages for a Cargo.lock file.",
    )
    parser.add_argument(
        "--cargo-lock",
        type=str,
        required=False,
        default=None,
        help="Path to the Cargo.lock file to use with `--cargo-lock-download`."
    )
    parser.add_argument(
        "--target-directory",
        type=str,
        required=False,
        default=None,
        help="Path to write the Cargo crate files to when using the `--cargo-lock-download` option."
    )

    parser.add_argument(
        "--log-level",
        type=log_level_type,
        required=False,
        default=logging.WARNING,
        help="Log level to use (name or integer). Defaults to ≥ warning."
    )

    arguments = parser.parse_args()
    configure_logging(level=arguments.log_level)

    if arguments.cargo_lock_download:
        from license_tools.tools import cargo_tools
        return cargo_tools.download_from_lock_file(
            lock_path=arguments.cargo_lock,
            target_directory=arguments.target_directory
        )

    from license_tools import retrieval
    retrieval.run(
        directory=arguments.directory,
        file_path=arguments.file,
        archive_path=arguments.archive,
        package_definition=arguments.package,
        download_url=arguments.url,
        index_url=arguments.index_url,
        prefer_sdist=arguments.prefer_sdist,
        job_count=arguments.jobs,
        retrieve_copyrights=arguments.retrieve_copyrights,
        retrieve_emails=arguments.retrieve_emails,
        retrieve_file_info=arguments.retrieve_file_info,
        retrieve_urls=arguments.retrieve_urls,
        retrieve_ldd_data=arguments.retrieve_ldd_data,
        retrieve_font_data=arguments.retrieve_font_data,
        retrieve_python_metadata=arguments.retrieve_python_metadata,
        retrieve_cargo_metadata=arguments.retrieve_cargo_metadata,
        retrieve_image_metadata=arguments.retrieve_image_metadata,
    )


if __name__ == "__main__":
    main()
