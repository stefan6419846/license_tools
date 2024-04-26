# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to Cargo/Rust.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

import tomli

from license_tools.utils import download_utils, rendering_utils
from license_tools.utils.download_utils import Download

logger = logging.getLogger(__name__)
del logging


# https://doc.rust-lang.org/cargo/reference/manifest.html
_VERBOSE_NAMES = {
    "name": "Name",
    "version": "Version",
    "authors": "Authors",
    "description": "Description",
    "readme": "README",
    "homepage": "Homepage",
    "repository": "Repository",
    "license": "License",
    "license-file": "License File",
    "keywords": "Keywords",
    "categories": "Categories",
}


def read_toml(path: Path) -> dict[str, Any]:
    """
    Read the given TOML file.

    :param path: The file to read.
    :return: The parsed file content.
    """
    return tomli.loads(path.read_text())


def analyze_metadata(path: Path | str) -> dict[str, str | list[str]] | None:
    """
    Analyze the Rust package metadata for the given directory.

    :param path: The directory/file to analyze. Should either be a directory or `Cargo.toml` file.
    :return: The package metadata.
    """
    path = Path(path)
    if path.name != "Cargo.toml":
        if path.joinpath("Cargo.toml").exists():
            path = path / "Cargo.toml"
        elif len(list(path.glob("*"))) == 1:
            path = next(path.glob("*")) / "Cargo.toml"
        else:
            raise ValueError(f"No clear Cargo.toml in {path}.")
    manifest = read_toml(path)
    return manifest.get("package")


def check_metadata(path: Path | str) -> str:
    """
    Render the relevant details for the given package.

    :param path: The package path.
    :return: The rendered dictionary-like representation of the relevant fields.
    """
    metadata = analyze_metadata(path)
    if not metadata:
        return ""
    return rendering_utils.render_dictionary(
        dictionary=metadata, verbose_names_mapping=_VERBOSE_NAMES, multi_value_keys={"authors", "categories", "keywords"}
    )


@dataclass
class PackageVersion:
    """
    Container for holding a package version.
    """

    name: str
    """
    The package name.
    """

    version: str
    """
    The package version.
    """

    checksum: str
    """
    The package checksum.
    """

    def to_download(self) -> Download:
        """
        Generate the corresponding download URL.

        :return: The corresponding download.
        """
        return Download(
            url=f"https://crates.io/api/v1/crates/{self.name}/{self.version}/download",
            filename=f"{self.name}_{self.version}.crate",
            sha256=self.checksum
        )


def get_package_versions(lock_path: Path | str) -> Generator[PackageVersion, None, None]:
    """
    Get the packages from the given lock file.

    :param lock_path: The lock file to read.
    :return: The packages retrieved from lock file.
    """
    data = read_toml(Path(lock_path))
    for package in data["package"]:
        if package.get("source") != "registry+https://github.com/rust-lang/crates.io-index":
            logger.warning("Skipping %s", package)
            continue
        yield PackageVersion(name=package["name"], version=package["version"], checksum=package["checksum"])


def download_from_lock_file(lock_path: Path | str, target_directory: Path | str) -> None:
    """
    Download the packages from the given lock file.

    :param lock_path: The lock file to read.
    :param target_directory: The directory to write the packages to.
    """
    target_directory = Path(target_directory)
    if not target_directory.exists():
        target_directory.mkdir()

    downloads = [package.to_download() for package in get_package_versions(lock_path)]
    download_utils.download_one_file_per_second(downloads=downloads, directory=target_directory)
