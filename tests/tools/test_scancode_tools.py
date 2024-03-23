# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import datetime
from pathlib import Path
from tempfile import mkdtemp, NamedTemporaryFile
from typing import cast, Dict
from unittest import TestCase

from license_tools.retrieval import RetrievalFlags
from license_tools.tools import scancode_tools
from license_tools.tools.scancode_tools import (
    Copyright,
    Copyrights,
    Emails,
    FileInfo,
    FileResults,
    Holder,
    LicenseDetection, LicenseMatch, Licenses,
    PackageResults, Party, Url,
    Urls,
)
from tests import get_from_url
from tests.data import LIBAIO1__0_3_109_1_25__RPM, LICENSE_PATH, SETUP_PATH, SETUP_PY_LICENSES


class LicensesTestCase(TestCase):
    def test_get_scores_of_detected_license_expression_spdx(self) -> None:
        result = SETUP_PY_LICENSES.get_scores_of_detected_license_expression_spdx()
        self.assertEqual([], result)

        file_results = FileResults(
            path=LICENSE_PATH, short_path="LICENSE.txt", retrieve_licenses=True
        )
        licenses = cast(Licenses, file_results.licenses)
        result = licenses.get_scores_of_detected_license_expression_spdx()
        self.assertEqual([100.0], result)


class FileResultsTestCase(TestCase):
    def assert_not_requested(
        self, result: FileResults, fields: list[str], invert: bool = False
    ) -> None:
        method = self.assertIsNotNone if invert else self.assertIsNone
        for field in fields:
            with self.subTest(field=field):
                method(getattr(result, field))

    def test_full(self) -> None:
        flags = cast(Dict[str, bool], RetrievalFlags.all(as_kwargs=True))
        del flags["retrieve_ldd_data"]
        del flags["retrieve_font_data"]
        del flags["retrieve_python_metadata"]
        self.assertEqual(4, len(flags))
        result = FileResults(
            path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True,
            retrieve_copyrights=flags["retrieve_copyrights"],
            retrieve_emails=flags["retrieve_emails"],
            retrieve_urls=flags["retrieve_urls"],
            retrieve_file_info=flags["retrieve_file_info"],
        )
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(
            result=result,
            fields=["copyrights", "emails", "urls", "licenses", "file_info"],
            invert=True,
        )

    def test_none(self) -> None:
        result = FileResults(path=Path("/tmp/dummy.py"), short_path="dummy.py")
        self.assertEqual(Path("/tmp/dummy.py"), result.path)
        self.assertEqual("dummy.py", result.short_path)
        self.assert_not_requested(
            result=result,
            fields=["copyrights", "emails", "urls", "licenses", "file_info"],
        )

    def test_retrieve_copyrights(self) -> None:
        result = scancode_tools.FileResults(
            path=SETUP_PATH, short_path="setup.py", retrieve_copyrights=True
        )
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(
            result=result, fields=["emails", "urls", "licenses", "file_info"]
        )
        expected = Copyrights(
            copyrights=[
                Copyright(
                    copyright="Copyright (c) stefan6419846", start_line=1, end_line=1
                )
            ],
            holders=[Holder(holder="stefan6419846", start_line=1, end_line=1)],
            authors=[],
        )
        self.assertEqual(expected, result.copyrights)

    def test_retrieve_emails(self) -> None:
        result = scancode_tools.FileResults(
            path=SETUP_PATH, short_path="setup.py", retrieve_emails=True
        )
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(
            result=result, fields=["copyrights", "urls", "licenses", "file_info"]
        )
        expected = Emails(emails=[])
        self.assertEqual(expected, result.emails)

    def test_retrieve_urls(self) -> None:
        result = scancode_tools.FileResults(
            path=SETUP_PATH, short_path="setup.py", retrieve_urls=True
        )
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(
            result=result, fields=["copyrights", "emails", "licenses", "file_info"]
        )
        expected = Urls(
            urls=[
                Url(
                    url="http://www.apache.org/licenses/LICENSE-2.0",
                    start_line=3,
                    end_line=3,
                ),
                Url(
                    url="https://github.com/stefan6419846/license_tools",
                    start_line=21,
                    end_line=21,
                ),
            ]
        )
        self.assertEqual(expected, result.urls)

    def test_retrieve_licenses(self) -> None:
        self.maxDiff = None
        result = scancode_tools.FileResults(
            path=SETUP_PATH, short_path="setup.py", retrieve_licenses=True
        )
        self.assertEqual(SETUP_PATH, result.path)
        self.assertEqual("setup.py", result.short_path)
        self.assert_not_requested(
            result=result, fields=["copyrights", "emails", "urls", "file_info"]
        )
        self.assertEqual(SETUP_PY_LICENSES, result.licenses)

    def test_retrieve_file_info(self) -> None:
        with NamedTemporaryFile(suffix=".py") as file_object:
            path = Path(file_object.name)
            path.write_text('print("Hello World!")\n')
            result = scancode_tools.FileResults(
                path=path, short_path="test.py", retrieve_file_info=True
            )

        self.assertEqual(path, result.path)
        self.assertEqual("test.py", result.short_path)
        self.assert_not_requested(
            result=result, fields=["copyrights", "emails", "urls", "licenses"]
        )
        expected = FileInfo(
            date=datetime.date.today(),
            size=22,
            sha1="e343a35cf2fa04782749dab102d45129cdb0b644",
            md5="a97c0affb458a65d8682bf0a48f36e63",
            sha256="c63bf759e5502fc9f4ad863b883423a2d75992aeaebee6a713eb81fe3f714a4b",
            mime_type="text/plain",
            file_type="ASCII text",
            programming_language="Python",
            is_binary=False,
            is_text=True,
            is_archive=False,
            is_media=False,
            is_source=True,
            is_script=False,
        )
        self.assertEqual(expected, result.file_info)


class PackageResultsTestCase(TestCase):
    def test_rpm(self) -> None:
        with get_from_url(LIBAIO1__0_3_109_1_25__RPM) as rpm_path:
            results = PackageResults.from_rpm(rpm_path)
        self.assertEqual(
            PackageResults(
                api_data_url=None, bug_tracking_url=None, code_view_url=None, copyright=None, datasource_id='rpm_archive',
                declared_license_expression='lgpl-2.1-plus', declared_license_expression_spdx='LGPL-2.1-or-later',
                description=(
                    'Linux-Native Asynchronous I/O Access Library\nThe Linux-native asynchronous I/O facility ("async I/O", or "aio") has\n'
                    'a richer API and capability set than the simple POSIX async I/O\nfacility. This library provides the Linux-native API for async I/O. '
                    'The\nPOSIX async I/O facility requires this library to provide\nkernel-accelerated async I/O capabilities, as do applications that\n'
                    'require the Linux-native async I/O API.'
                ),
                download_url=None, extracted_license_statement='LGPL-2.1+', holder=None,
                homepage_url='http://kernel.org/pub/linux/libs/aio/', keywords=[],
                license_detections=[
                    LicenseDetection(
                        license_expression='lgpl-2.1-plus', license_expression_spdx='LGPL-2.1-or-later',
                        identifier='lgpl_2_1_plus-d0bddf88-13b4-4982-bdf5-ce866a0e8394',
                        matches=[
                            LicenseMatch(
                                score=100.0, start_line=1, end_line=1, matched_length=3, match_coverage=100.0, matcher='1-hash',
                                license_expression='lgpl-2.1-plus', rule_identifier='lgpl-2.1-plus_64.RULE', rule_relevance=100,
                                rule_url='https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/lgpl-2.1-plus_64.RULE',
                                matched_text='LGPL-2.1+',
                                spdx_license_expression='LGPL-2.1-or-later', from_file=None,
                            )
                        ]
                    )
                ],
                md5=None, name='libaio1', namespace=None, notice_text=None, other_license_detections=[], other_license_expression=None,
                other_license_expression_spdx=None,
                parties=[
                    Party(type=None, role='distributor', name='SUSE Linux Enterprise 15', email=None, url=None),
                    Party(type=None, role='vendor', name='SUSE LLC <https://www.suse.com/>', email=None, url=None)
                ],
                primary_language=None, purl='pkg:rpm/libaio1@0.3.109-1.25', qualifiers={}, release_date=None,
                repository_download_url=None, repository_homepage_url=None, sha1=None, sha256=None, sha512=None, size=None,
                source_packages=['pkg:rpm/libaio@0.3.109-1.25?arch=src'], subpath=None, type='rpm', vcs_url=None, version='0.3.109-1.25'
            ),
            results
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
