# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

from unittest import TestCase

from license_tools.tools import translation_tools
from tests import get_file, get_from_url
from tests.data import DJANGO__5076BB4__DJANGO_MO, DJANGO__5076BB4__DJANGO_PO, LICENSE_PATH, SETUP_PATH


class IsCompiledGettextFileTestCase(TestCase):
    def test_is_compiled_gettext_file(self) -> None:
        self.assertFalse(translation_tools.is_compiled_gettext_file(SETUP_PATH))
        self.assertFalse(translation_tools.is_compiled_gettext_file(LICENSE_PATH))

        with get_file("Carlito-Regular.ttf") as path:
            self.assertFalse(translation_tools.is_compiled_gettext_file(path))

        with get_file("croissant.jpg") as path:
            self.assertFalse(translation_tools.is_compiled_gettext_file(path))

        with get_from_url(DJANGO__5076BB4__DJANGO_MO) as path:
            self.assertTrue(translation_tools.is_compiled_gettext_file(path))

        with get_from_url(DJANGO__5076BB4__DJANGO_PO) as path:
            self.assertFalse(translation_tools.is_compiled_gettext_file(path))


class CheckCompiledGettextMetadataTestCase(TestCase):
    maxDiff = None

    def test_python(self) -> None:
        self.assertIsNone(translation_tools.check_compiled_gettext_metadata(SETUP_PATH))

    def test_font(self) -> None:
        with get_file("Carlito-Regular.ttf") as path:
            self.assertIsNone(translation_tools.check_compiled_gettext_metadata(path))

    def test_django_mo(self) -> None:
        with get_from_url(DJANGO__5076BB4__DJANGO_MO) as path:
            result = translation_tools.check_compiled_gettext_metadata(path)

        self.assertIsNotNone(result)

        with get_file("django_mo.po") as path:
            self.assertEqual(path.read_text(), result)
