# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import argparse

from license_tools import retrieval


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
        "--package", action="store", type=str, help="Python package specification to use."
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

    arguments = parser.parse_args()

    retrieval.run(
        directory=arguments.directory,
        file_path=arguments.file,
        archive_path=arguments.archive,
        package_definition=arguments.package,
        download_url=arguments.url,
        index_url=arguments.index_url,
        job_count=arguments.jobs,
        retrieve_copyrights=arguments.retrieve_copyrights,
        retrieve_emails=arguments.retrieve_emails,
        retrieve_file_info=arguments.retrieve_file_info,
        retrieve_urls=arguments.retrieve_urls,
        retrieve_ldd_data=arguments.retrieve_ldd_data,
        retrieve_font_data=arguments.retrieve_font_data,
    )


if __name__ == "__main__":
    main()
