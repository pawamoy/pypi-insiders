# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2023, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Tests for the former public module paths."""

# YORE: Bump 2: Remove file.

from __future__ import annotations

import importlib
import re

import pytest


@pytest.mark.parametrize(
    ("module", "name"),
    [
        ("cli", "get_parser"),
        ("cli.repos", "run_repos"),
        ("cli.server", "run_server"),
        ("cli.update", "run_update"),
        ("cli.watcher", "run_watcher"),
        ("defaults", "DEFAULT_PORT"),
        ("logger", "logger"),
        ("repos", "RepositoryConfig"),
        ("server", "DistCollection"),
        ("update", "update_packages"),
        ("watcher", "GracefulExit"),
    ],
)
def test_legacy_module_forwards_attribute_with_warning(module: str, name: str) -> None:
    """Old module paths warn and return the object from its new location."""
    old_path = f"pypi_insiders.{module}"
    new_path = f"pypi_insiders._internal.{module}"
    old_module = importlib.import_module(old_path)
    new_module = importlib.import_module(new_path)

    warning = rf"Importing from `{re.escape(old_path)}` is deprecated\. Import from `{re.escape(new_path)}` instead\."
    with pytest.warns(DeprecationWarning, match=warning):
        old_object = getattr(old_module, name)

    assert old_object is getattr(new_module, name)
