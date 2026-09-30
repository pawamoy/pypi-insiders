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

"""Tests for the CLI."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from pypi_insiders import main
from pypi_insiders._internal import debug

if TYPE_CHECKING:
    from pathlib import Path


def test_main() -> None:
    """Return an error when no command is given."""
    assert main([]) == 1


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["-h"])
    captured = capsys.readouterr()
    assert "pypi-insiders" in captured.out


@pytest.mark.xfail
def test_server_commands() -> None:
    """Server commands."""
    assert main(["server", "start", "--port=31412"]) == 0
    time.sleep(5)
    assert main(["server", "status", "--port=31412"]) == 0
    assert main(["server", "stop", "--port=31412"]) == 0
    time.sleep(5)
    assert main(["server", "status", "--port=31412"]) == 0


@pytest.mark.xfail
def test_watcher_commands(tmp_path: Path) -> None:
    """Watcher commands.

    Parameters:
        tmp_path: A temporary directory path.
    """
    assert (
        main(
            [
                "watcher",
                "start",
                f"--conf-path={tmp_path / 'repos.json'}",
                f"--repo-dir={tmp_path / 'repos'}",
                "--index-url=http://localhost:9999",
                "--sleep=10",
            ],
        )
        == 0
    )
    time.sleep(5)
    assert main(["watcher", "status"]) == 0
    assert main(["watcher", "stop"]) == 0
    assert main(["watcher", "status"]) == 0


@pytest.mark.xfail
def test_update_command(tmp_path: Path) -> None:
    """Update command.

    Parameters:
        tmp_path: A temporary directory path.
    """
    main(
        [
            "repos",
            "add",
            "pawamoy-insiders/pypi-insiders:pypi-insiders",
            f"--conf-path={tmp_path / 'repos.json'}",
        ],
    )
    main(["server", "start", "--port=31413", f"--dist-dir={tmp_path / 'dists'}"])
    time.sleep(5)
    assert (
        main(
            [
                "update",
                f"--conf-path={tmp_path / 'repos.json'}",
                f"--repo-dir={tmp_path / 'repos'}",
                "--index-url=http://localhost:31413",
            ],
        )
        == 0
    )
    main(["server", "stop", "--port=31413"])


def test_repos_commands(tmp_path: Path) -> None:
    """Repos commands.

    Parameters:
        tmp_path: A temporary directory path.
    """
    assert (
        main(
            [
                "repos",
                "add",
                "namespace/project1:package1",
                "namespace/project2:package2",
                f"--conf-path={tmp_path / 'repos.json'}",
            ],
        )
        == 0
    )
    assert main(["repos", "list", f"--conf-path={tmp_path / 'repos.json'}"]) == 0
    assert (
        main(
            [
                "repos",
                "remove",
                "namespace/project1",
                f"--conf-path={tmp_path / 'repos.json'}",
                f"--repo-dir={tmp_path / 'repos'}",
            ],
        )
        == 0
    )


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["-V"])
    captured = capsys.readouterr()
    assert debug._get_version() in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
