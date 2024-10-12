"""Logic for the PyPI server."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import psutil
from twine.commands.upload import upload
from twine.settings import Settings
from unearth import PackageFinder

from pypi_insiders.defaults import DEFAULT_DIST_DIR, DEFAULT_INDEX_URL, DEFAULT_PORT
from pypi_insiders.logger import logger, redirect_output_to_logging, tail

if TYPE_CHECKING:
    from collections.abc import Iterable


class DistCollection:
    """Manage distributions."""

    def __init__(self, index_url: str = DEFAULT_INDEX_URL) -> None:
        """Initialize the instance.

        Parameters:
            index_url: The URL of the PyPI index to use.
        """
        self.index_url: str = index_url
        self._finder = PackageFinder(index_urls=[f"{self.index_url}/simple"])

    def latest_version(self, package: str) -> str | None:
        """Get the latest version of a package.

        Parameters:
            package: The package name (distribution name).

        Returns:
            The version as a string, or none.
        """
        result = self._finder.find_best_match(package, allow_prereleases=True, allow_yanked=True)
        return result.best.version if result.best else None

    def version_exists(self, package: str, version: str) -> bool:
        """Tell if a package version exists.

        Parameters:
            package: The package name (distribution name).
            version: The package version.

        Returns:
            True or False.
        """
        result = self._finder.find_best_match(f"{package}=={version}", allow_prereleases=True, allow_yanked=True)
        return bool(result.best)

    def upload(self, dists: Iterable[str | Path]) -> None:
        """Upload distributions.

        Parameters:
            dists: The distributions to upload.
        """
        with redirect_output_to_logging(stdout_level="debug"):
            upload(
                Settings(
                    non_interactive=True,
                    skip_existing=True,
                    repository_url=self.index_url,
                    username="",
                    password="",
                    disable_progress_bar=True,
                    verbose=True,
                ),
                [str(dist) for dist in dists],
            )


def start_server(
    *,
    dist_dir: str | Path = DEFAULT_DIST_DIR,
    port: int = DEFAULT_PORT,
) -> None:
    """Start the watcher in the background.

    Parameters:
        dist_dir: The directory that will receive the distribution artifacts.
        port: The server port.
    """
    logs_dir = tempfile.mkdtemp(prefix="pypi-insiders-server-")
    logs_file = Path(logs_dir) / "server.log"
    logger.info(f"Server logs: {logs_file}")
    subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-Impypi_insiders",
            "server",
            "run",
            f"--dist-dir={dist_dir}",
            f"--port={port}",
            "--log-level=debug",
            "--log-path",
            logs_file,
        ],
    )


def stop_server(*, port: int = 31411) -> bool:
    """Stop the server.

    Parameters:
        port: The server port.

    Returns:
        Whether a process was killed or not.
    """
    for proc in psutil.process_iter():
        try:
            cmdline = " ".join(proc.cmdline())
        except psutil.Error:
            continue
        if "pypi_insiders server run" in cmdline and f"--port={port}" in cmdline:
            proc.kill()
            return True
    return False


def server_status(*, port: int = 31411) -> dict | None:
    """Return the server status as a dict of metadata.

    Parameters:
        port: The server port.

    Returns:
        Some metadata about the server process.
    """
    for proc in psutil.process_iter():
        try:
            cmdline = " ".join(proc.cmdline())
        except psutil.Error:
            continue
        if "pypi_insiders server run" in cmdline and f"--port={port}" in cmdline:
            return proc.as_dict(attrs=("ppid", "create_time", "username", "name", "cmdline", "pid"))
    return None


def server_loop(
    *,
    dist_dir: str | Path = DEFAULT_DIST_DIR,
    port: int = DEFAULT_PORT,
) -> None:
    """Run the server in the foreground.

    Parameters:
        dist_dir: The directory that will receive the distribution artifacts.
        port: The server port.
    """
    from pypiserver.__main__ import main as serve

    Path(dist_dir).mkdir(parents=True, exist_ok=True)
    with redirect_output_to_logging():
        serve(
            [
                "run",
                str(dist_dir),
                f"-p{port}",
                "-a.",
                "-P.",
                "-vv",
            ],
        )


def server_logs(*, port: int = 31411) -> None:
    """Show the server logs.

    Parameters:
        port: The server port.
    """
    status = server_status(port=port)
    if not status:
        return
    tail(status["cmdline"][-1])
