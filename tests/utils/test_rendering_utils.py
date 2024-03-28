# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

from unittest import TestCase

from license_tools.utils import rendering_utils


class RenderDictionaryTestCase(TestCase):
    def test_render_dictionary(self) -> None:
        dictionary = {
            "key": "value",
            "pi": 3.141592653589793,
            "answer": 42,
            "key1": [1, 2, 3],
            "key2": (1, 2, 3),
            "key3": {3, 2, 1},
            "key4": {"foo": "bar"},
            "ignore": "me",
            "multi1": 1337,
            "multi2": [42, 43, 44],
        }
        mapping = {
            "key": "Key",
            "pi": "π",
            "answer": "Answer",
            "key1": "Key 1",
            "key2": "Key 2",
            "key3": "Key 3",
            "key4": "Key 4",
            "multi1": "Multiple 1",
            "multi2": "Multiple 2",
        }

        result = rendering_utils.render_dictionary(
            dictionary=dictionary,
            verbose_names_mapping=mapping,
            multi_value_keys={"key1", "key2", "key3", "multi1"},
        )
        self.assertEqual(
            """
       Key: value
         π: 3.141592653589793
    Answer: 42
     Key 1:
             * 1
             * 2
             * 3
     Key 2:
             * 1
             * 2
             * 3
     Key 3:
             * 1
             * 2
             * 3
     Key 4: {'foo': 'bar'}
Multiple 1: 1337
Multiple 2: [42, 43, 44]
"""[1:-1],
            result
        )
