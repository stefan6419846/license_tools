# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Rendering utilities.
"""

from __future__ import annotations

from typing import Any


def render_dictionary(dictionary: dict[str, Any], verbose_names_mapping: dict[str, str], multi_value_keys: set[str]) -> str:
    """
    Render the given dictionary as string.

    :param dictionary: The dictionary to render.
    :param verbose_names_mapping: The mapping dictionary to use for the keys.
                                  Keys not available inside this dictionary will be skipped.
    :param multi_value_keys: Dictionary keys which could have multiple values.
    """
    maximum_length = max(map(len, verbose_names_mapping.values()))
    rendered = []
    for key, verbose_name in verbose_names_mapping.items():
        if key not in dictionary:
            continue
        value = dictionary[key]
        if key in multi_value_keys and isinstance(value, (list, set, tuple)):
            if isinstance(value, tuple):
                value = list(value)
            if len(value) == 1:
                value = value.pop()
                rendered.append(f"{verbose_name:>{maximum_length}}: {value}")
            elif not value:
                rendered.append(f"{verbose_name:>{maximum_length}}:")
            else:
                value = "\n" + "\n".join(map(lambda x: " " * maximum_length + f"   * {x}", sorted(value)))
                rendered.append(f"{verbose_name:>{maximum_length}}:{value}")
        else:
            rendered.append(f"{verbose_name:>{maximum_length}}: {value}")
    return "\n".join(rendered)
