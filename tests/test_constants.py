# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

from unittest import TestCase

from license_tools import constants


class ConstantsTestCase(TestCase):
    def test_version(self) -> None:
        self.assertIsNotNone(constants.VERSION)
