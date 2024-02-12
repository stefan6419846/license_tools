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
    matched_text: str | None = None


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

    detected_license_expression: str | None = None
    detected_license_expression_spdx: str | None = None
    percentage_of_license_text: float = 0.0
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
    copyrights: Copyrights | None = None
    emails: Emails | None = None
    urls: Urls | None = None
    licenses: Licenses | None = None
    file_info: FileInfo | None = None

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

    type: PARTY_TYPES = None
    role: str | None = None
    name: str | None = None
    email: str | None = None
    url: str | None = None


@dataclass
class PackageResults:
    """
    Container for package-specific data, based upon `packagedcode.models.PackageData`.
    """

    api_data_url: str | None = None
    bug_tracking_url: str | None = None
    code_view_url: str | None = None
    copyright: str | None = None
    datasource_id: str | None = None
    declared_license_expression: str | None = None
    declared_license_expression_spdx: str | None = None
    # dependencies: list[DependentPackage] = dataclass_field(default_factory=list)
    description: str | None = None
    download_url: str | None = None
    # extra_data: dict[str, Any] = dataclass_field(default_factory=dict)
    extracted_license_statement: str | None = None
    # file_references: list[FileReference] = dataclass_field(default_factory=list)
    holder: str | None = None
    homepage_url: str | None = None
    keywords: list[str] = dataclass_field(default_factory=list)
    license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    md5: str | None = None
    name: str | None = None
    namespace: str | None = None
    notice_text: str | None = None
    other_license_detections: list[LicenseDetection] = dataclass_field(default_factory=list)
    other_license_expression: str | None = None
    other_license_expression_spdx: str | None = None
    parties: list[Party] = dataclass_field(default_factory=list)
    primary_language: str | None = None
    purl: str | None = None
    qualifiers: dict[str, str] = dataclass_field(default_factory=dict)
    release_date: datetime.date | None = None
    repository_download_url: str | None = None
    repository_homepage_url: str | None = None
    sha1: str | None = None
    sha256: str | None = None
    sha512: str | None = None
    size: int | None = None
    source_packages: list[str] | None = None
    subpath: str | None = None
    type: str | None = None
    vcs_url: str | None = None
    version: str | None = None

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
    def from_rpm(cls, path: Path) -> 'PackageResults':
        # Drop some keys which we do not handle for now.
        data = next(RpmArchiveHandler.parse(path)).to_dict()
        data.pop('dependencies', None)
        data.pop('extra_data', None)
        data.pop('file_references', None)
        return cls(**data)


def cleanup(directory: Path | str) -> None:
    """
    Remove the given directory.
    """
    fileutils.delete(directory)


atexit.register(cleanup, scancode_config.scancode_temp_dir)
