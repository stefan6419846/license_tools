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
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Literal

import scancode_config  # type: ignore[import-untyped]
from commoncode import fileutils  # type: ignore[import-untyped]
from packagedcode.rpm import RpmArchiveHandler  # type: ignore[import-untyped]
from scancode import api  # type: ignore[import-untyped]


@dataclass
class Author:
    """
    Matching information about an author.
    """

    author: str
    """
    The author name.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """


@dataclass
class Holder:
    """
    Matching information about a copyright holder.
    """

    holder: str
    """
    The copyright holder.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """


@dataclass
class Copyright:
    """
    Matching information about copyrights.
    """

    copyright: str
    """
    The copyright statement.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """


@dataclass
class Copyrights:
    """
    Copyright-specific results.
    """

    copyrights: list[Copyright] = dataclass_field(default_factory=list)
    """
    The detected copyright statements.
    """

    holders: list[Holder] = dataclass_field(default_factory=list)
    """
    The detected copyright holders.
    """

    authors: list[Author] = dataclass_field(default_factory=list)
    """
    The detected authors.
    """

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
    """
    The e-mail address.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """


@dataclass
class Emails:
    """
    E-mail-specific results.
    """

    emails: list[Email] = dataclass_field(default_factory=list)
    """
    The detected e-mail addresses.
    """

    def __post_init__(self) -> None:
        self.emails = [Email(**x) if not isinstance(x, Email) else x for x in self.emails]  # type: ignore[arg-type]


@dataclass
class Url:
    """
    Matching information about an URL.
    """

    url: str
    """
    The URL.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """


@dataclass
class Urls:
    """
    URL-specific results.
    """

    urls: list[Url] = dataclass_field(default_factory=list)
    """
    The detected URLs.
    """

    def __post_init__(self) -> None:
        self.urls = [Url(**x) if not isinstance(x, Url) else x for x in self.urls]  # type: ignore[arg-type]


@dataclass
class FileInfo:
    """
    File-specific results.
    """

    date: datetime.date
    """
    The modification date.
    """

    size: int
    """
    The file size in bytes.
    """

    sha1: str | None
    """
    The SHA1 hash.
    """

    md5: str | None
    """
    The MD5 hash.
    """

    sha256: str | None
    """
    The SHA256 hash.
    """

    mime_type: str
    """
    The detected mime type.
    """

    file_type: str
    """
    The detected file type.
    """

    programming_language: str | None
    """
    The detected programming language.
    """

    is_binary: bool
    """
    Whether this file is a binary one.
    """

    is_text: bool
    """
    Whether this file is a plaintext one.
    """

    is_archive: bool
    """
    Whether this file is an archive.
    """

    is_media: bool
    """
    Whether this is some media file.
    """

    is_source: bool
    """
    Whether this is some source code file.
    """

    is_script: bool
    """
    Whether this file is some script.
    """

    def __post_init__(self) -> None:
        if isinstance(self.date, str):
            self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d").date()


@dataclass
class LicenseMatch:
    """
    Matching information about a license.
    """

    score: float
    """
    The matching score.
    """

    start_line: int
    """
    The corresponding start line.
    """

    end_line: int
    """
    The corresponding end line.
    """

    matched_length: int
    """
    The length of the match in bytes/characters.
    """

    match_coverage: float
    """
    How much of the rule text is part of the match?
    """

    matcher: str
    """
    The corresponding matcher type.
    """

    license_expression: str
    """
    The detected license expression.
    """

    license_expression_spdx: str
    """
    The detected license expression in SPDX format.
    """

    rule_identifier: str
    """
    The corresponding matcher rule.
    """

    rule_relevance: int
    """
    The relevance of the corresponding rule.
    """

    rule_url: str | None
    """
    Upstream link for this rule.
    """

    from_file: str | None
    """
    Unused/unclear.
    """

    matched_text: str | None = None
    """
    The text of the match.
    """


@dataclass
class LicenseClue(LicenseMatch):
    """
    Matching information about a license. Compared to regular detections/matches, these are rather
    considered clues and not perfect detections.

    Currently the same as :class:`~LicenseMatch`.
    """

    pass


@dataclass
class LicenseDetection:
    """
    Information on a specific detected license.
    """

    license_expression: str
    """
    The detected license expression.
    """

    license_expression_spdx: str
    """
    The detected license expression in SPDX format.
    """

    identifier: str
    """
    An unique ID for this detection.
    """

    matches: list[LicenseMatch] = dataclass_field(default_factory=list)
    """
    The corresponding detailed match data.
    """

    def __post_init__(self) -> None:
        self.matches = [LicenseMatch(**x) if not isinstance(x, LicenseMatch) else x for x in self.matches]  # type: ignore[arg-type]


@dataclass
class Licenses:
    """
    Information on all detected licenses.
    """

    detected_license_expression: str | None = None
    """
    The detected license expression.
    """

    detected_license_expression_spdx: str | None = None
    """
    The detected license expression in SPDX format.
    """

    percentage_of_license_text: float = 0.0
    """
    How much of the file content is part of the license text?
    """

    license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    """
    The corresponding license detections.
    """

    license_clues: list[LicenseClue] = dataclass_field(default_factory=list)
    """
    The corresponding license clues.
    """

    def __post_init__(self) -> None:
        self.license_detections = [
            LicenseDetection(**x) if not isinstance(x, LicenseDetection) else x for x in self.license_detections  # type: ignore[arg-type]
        ]
        self.license_clues = [
            LicenseClue(**x) if not isinstance(x, LicenseClue) else x for x in self.license_clues  # type: ignore[arg-type]
        ]

    def get_scores_of_detected_license_expression_spdx(self) -> list[float]:
        """
        Attempt to resolve the scores for the detected license expression.

        :return: The corresponding scores if they could be resolved.
        """
        scores = []
        for detection in self.license_detections:
            if (
                detection.license_expression == self.detected_license_expression
                or detection.license_expression_spdx
                == self.detected_license_expression_spdx
            ):
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
    """
    Full path of the analyzed file.
    """

    short_path: str
    """
    Short path of the analyzed file, with the common prefix removed.
    """

    # Configuration values to determine which information to retrieve.
    retrieve_copyrights: bool = False
    """
    Configuration option: Whether to retrieve copyright information.
    """

    retrieve_emails: bool = False
    """
    Configuration option: Whether to retrieve e-mail addresses.
    """

    retrieve_urls: bool = False
    """
    Configuration option: Whether to retrieve URLs.
    """

    retrieve_licenses: bool = False
    """
    Configuration option: Whether to retrieve license information.
    """

    retrieve_file_info: bool = False
    """
    Configuration option: Whether to retrieve file information.
    """

    # Analysis results.
    copyrights: Copyrights | None = None
    """
    The detected copyrights.
    """

    emails: Emails | None = None
    """
    The detected e-mail addresses.
    """

    urls: Urls | None = None
    """
    The detected URLs.
    """

    licenses: Licenses | None = None
    """
    The detected licenses.
    """

    file_info: FileInfo | None = None
    """
    The retrieved file information.
    """

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


@dataclass
class Party:
    """
    A party related to a package.
    """

    PARTY_TYPES = Literal[None, "person", "project", "organization"]
    """
    Available party types.
    """

    type: PARTY_TYPES = None
    """
    The party type.
    """

    role: str | None = None
    """
    The associated role.
    """

    name: str | None = None
    """
    The corresponding name.
    """

    email: str | None = None
    """
    The corresponding e-mail address.
    """

    url: str | None = None
    """
    The corresponding URL/webpage.
    """


@dataclass
class PackageResults:
    """
    Container for package-specific data, based upon ``packagedcode.models.PackageData``.
    """

    api_data_url: str | None = None
    """
    API URL to obtain structured data for this package.
    """

    bug_tracking_url: str | None = None
    """
    URL to the issue or bug tracker.
    """

    code_view_url: str | None = None
    """
    An URL where th ecode can be browsed online.
    """

    copyright: str | None = None
    """
    Copyright statements for this package.
    """

    datasource_id: str | None = None
    """
    Data source identifier for the source of the package data.
    """

    declared_license_expression: str | None = None
    """
    License expression derived from metadata.
    """

    declared_license_expression_spdx: str | None = None
    """
    License expression derived from metadata in SPDX format.
    """

    # dependencies: list[DependentPackage] = dataclass_field(default_factory=list)
    description: str | None = None
    """
    Description for this package.
    """

    download_url: str | None = None
    """
    A direct download URL.
    """

    # extra_data: dict[str, Any] = dataclass_field(default_factory=dict)
    extracted_license_statement: str | None = None
    """
    License statement extracted from the metadata.
    """

    # file_references: list[FileReference] = dataclass_field(default_factory=list)
    holder: str | None = None
    """
    Copyright holders for this package.
    """

    homepage_url: str | None = None
    """
    URL to the homepage.
    """

    keywords: list[str] = dataclass_field(default_factory=list)
    """
    Associated keywords.
    """

    license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    """
    Detected licenses.
    """

    md5: str | None = None
    """
    MD5 checksum.
    """

    name: str | None = None
    """
    Package name.
    """

    namespace: str | None = None
    """
    Package namespace.
    """

    notice_text: str | None = None
    """
    Corresponding notice text.
    """

    other_license_detections: list[LicenseDetection] = dataclass_field(
        default_factory=list
    )
    """
    Additional license detections.
    """

    other_license_expression: str | None = None
    """
    Another/a secondary license derived from the metadata.
    """

    other_license_expression_spdx: str | None = None
    """
    Another/a secondary license derived from the metadata in SPDX format.
    """

    parties: list[Party] = dataclass_field(default_factory=list)
    """
    Parties such as a person, project or organization.
    """

    primary_language: str | None = None
    """
    Primary programming language.
    """

    purl: str | None = None
    """
    Corresponding PURL identifier.
    """

    qualifiers: dict[str, str] = dataclass_field(default_factory=dict)
    """
    Mapping of package qualifiers.
    """

    release_date: datetime.date | None = None
    """
    Release date of the package.
    """

    repository_download_url: str | None = None
    """
    Download URL for this package in its package repository.
    """

    repository_homepage_url: str | None = None
    """
    URL to the page for this package in its package repository.
    """

    sha1: str | None = None
    """
    SHA1 checksum.
    """

    sha256: str | None = None
    """
    SHA256 checksum.
    """

    sha512: str | None = None
    """
    SHA512 checksum.
    """

    size: int | None = None
    """
    Size of the package download in bytes.
    """

    source_packages: list[str] | None = None
    """
    PURLs for related source packages.
    """

    subpath: str | None = None
    """
    Subpath inside a package, relative to its root.
    """

    type: str | None = None
    """
    Short code for package type.
    """

    vcs_url: str | None = None
    """
    An URL to the VCS repository in SPDX format.
    """

    version: str | None = None
    """
    Package version.
    """

    is_virtual: bool = False
    """
    Indicate virtual packages.
    """

    is_private: bool = False
    """
    Indicate private packages.
    """

    def __post_init__(self) -> None:
        self.license_detections = [
            LicenseDetection(**x) if not isinstance(x, LicenseDetection) else x for x in self.license_detections  # type: ignore[arg-type]
        ]
        self.other_license_detections = [
            LicenseDetection(**x) if not isinstance(x, LicenseDetection) else x for x in self.other_license_detections  # type: ignore[arg-type]
        ]
        self.parties = [
            Party(**x) if not isinstance(x, Party) else x for x in self.parties  # type: ignore[arg-type]
        ]

    @classmethod
    def from_rpm(cls, path: Path) -> "PackageResults":
        """
        Get the results for the given RPM path.

        :param path: The RPM path to run on.
        :return: The corresponding results.
        """
        # Drop some keys which we do not handle for now.
        data = next(RpmArchiveHandler.parse(path)).to_dict()
        data.pop("dependencies", None)
        data.pop("extra_data", None)
        data.pop("file_references", None)
        return cls(**data)


def cleanup(directory: Path | str) -> None:
    """
    Remove the given directory.
    """
    fileutils.delete(directory)


atexit.register(cleanup, scancode_config.scancode_temp_dir)
