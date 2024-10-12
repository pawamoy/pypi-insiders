"""Tests for the `cli` module."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from pypi_insiders import cli, debug

if TYPE_CHECKING:
    from pathlib import Path


def test_main() -> None:
    """Basic CLI test."""
    assert cli.main([]) == 1


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "pypi-insiders" in captured.out


@pytest.mark.xfail
def test_server_commands() -> None:
    """Server commands."""
    assert cli.main(["server", "start", "--port=31412"]) == 0
    time.sleep(5)
    assert cli.main(["server", "status", "--port=31412"]) == 0
    assert cli.main(["server", "stop", "--port=31412"]) == 0
    time.sleep(5)
    assert cli.main(["server", "status", "--port=31412"]) == 0


@pytest.mark.xfail
def test_watcher_commands(tmp_path: Path) -> None:
    """Watcher commands.

    Parameters:
        tmp_path: A temporary directory path.
    """
    assert (
        cli.main(
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
    assert cli.main(["watcher", "status"]) == 0
    assert cli.main(["watcher", "stop"]) == 0
    assert cli.main(["watcher", "status"]) == 0


@pytest.mark.xfail
def test_update_command(tmp_path: Path) -> None:
    """Update command.

    Parameters:
        tmp_path: A temporary directory path.
    """
    cli.main(
        [
            "repos",
            "add",
            "pawamoy-insiders/pypi-insiders:pypi-insiders",
            f"--conf-path={tmp_path / 'repos.json'}",
        ],
    )
    cli.main(["server", "start", "--port=31413", f"--dist-dir={tmp_path / 'dists'}"])
    time.sleep(5)
    assert (
        cli.main(
            [
                "update",
                f"--conf-path={tmp_path / 'repos.json'}",
                f"--repo-dir={tmp_path / 'repos'}",
                "--index-url=http://localhost:31413",
            ],
        )
        == 0
    )
    cli.main(["server", "stop", "--port=31413"])


def test_repos_commands(tmp_path: Path) -> None:
    """Repos commands.

    Parameters:
        tmp_path: A temporary directory path.
    """
    assert (
        cli.main(
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
    assert cli.main(["repos", "list", f"--conf-path={tmp_path / 'repos.json'}"]) == 0
    assert cli.main(["repos", "remove", "namespace/project1", f"--conf-path={tmp_path / 'repos.json'}"]) == 0


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-V"])
    captured = capsys.readouterr()
    assert debug.get_version() in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
