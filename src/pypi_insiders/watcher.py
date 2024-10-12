"""Repositories watcher."""

from __future__ import annotations

import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

import psutil

from pypi_insiders.defaults import DEFAULT_CONF_PATH, DEFAULT_INDEX_URL, DEFAULT_REPO_DIR, DEFAULT_WATCHER_SLEEP
from pypi_insiders.logger import logger, tail
from pypi_insiders.repos import RepositoryConfig
from pypi_insiders.update import update_packages

if TYPE_CHECKING:
    from types import FrameType


class GracefulExit:
    """Signal handler to exit gracefully."""

    def __init__(self) -> None:
        """Initialize the handler."""
        self.sleeping = False
        self.received_signal = False
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)

    def __bool__(self) -> bool:
        return self.received_signal

    def _exit_gracefully(self, signum: int, frame: FrameType | None) -> None:  # noqa: ARG002
        if self.sleeping:
            # we were sleeping, it's fine to exit
            sys.exit(0)
        if self.received_signal:
            # received a second time, force exit
            sys.exit(1)
        self.received_signal = True

    def sleep(self, seconds: int) -> None:
        """Sleep for a bit.

        Parameters:
            seconds: Number of seconds of sleep.
        """
        self.sleeping = True
        time.sleep(seconds)
        self.sleeping = False


def start_watcher(
    *,
    conf_path: str | Path = DEFAULT_CONF_PATH,
    repo_dir: str | Path = DEFAULT_REPO_DIR,
    index_url: str = DEFAULT_INDEX_URL,
    sleep: int = DEFAULT_WATCHER_SLEEP,
) -> None:
    """Start the watcher in the background.

    Parameters:
        conf_path: The path to the configuration file.
        repo_dir: The directory in which the repositories are cloned.
        index_url: The URL of the PyPI index to upload to.
        sleep: The time to sleep in between iterations, in seconds.
    """
    Path(repo_dir).mkdir(parents=True, exist_ok=True)
    logs_dir = tempfile.mkdtemp(prefix="pypi-insiders-watcher-")
    logs_file = Path(logs_dir) / "watcher.log"
    logger.info(f"Watcher logs: {logs_file}")
    subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-Impypi_insiders",
            "watcher",
            "run",
            f"--conf-path={conf_path}",
            f"--repo-dir={repo_dir}",
            f"--index-url={index_url}",
            f"--sleep={sleep}",
            "--log-level=debug",
            "--log-path",
            logs_file,
        ],
    )


def stop_watcher() -> bool:
    """Stop the watcher.

    Returns:
        Whether a process was killed or not.
    """
    for proc in psutil.process_iter():
        try:
            cmdline = " ".join(proc.cmdline())
        except psutil.Error:
            continue
        if "pypi_insiders watcher run" in cmdline:
            proc.kill()
            return True
    return False


def watcher_status() -> dict | None:
    """Return the watcher status as a dict of metadata.

    Returns:
        Some metadata about the watcher process.
    """
    for proc in psutil.process_iter():
        try:
            cmdline = " ".join(proc.cmdline())
        except psutil.Error:
            continue
        if "pypi_insiders watcher run" in cmdline:
            return proc.as_dict(attrs=("ppid", "create_time", "username", "name", "cmdline", "pid"))
    return None


def watcher_loop(
    *,
    conf_path: str | Path = DEFAULT_CONF_PATH,
    repo_dir: str | Path = DEFAULT_REPO_DIR,
    index_url: str = DEFAULT_INDEX_URL,
    sleep: int = DEFAULT_WATCHER_SLEEP,
) -> None:
    """Run the watcher in the foreground.

    Parameters:
        conf_path: The path to the configuration file.
        repo_dir: The directory containing the repository clones.
        index_url: The URL of the PyPI index to upload to.
        sleep: The time to sleep in between iterations, in seconds.
    """
    graceful_exit = GracefulExit()
    config = RepositoryConfig(conf_path)
    while True:
        for repo in config.get_repositories():
            update_packages(conf_path=conf_path, repo_dir=repo_dir, index_url=index_url, repos=[repo])
            if graceful_exit:
                break
        if graceful_exit:
            break
        graceful_exit.sleep(sleep)


def watcher_logs() -> None:
    """Show the watcher logs."""
    status = watcher_status()
    if not status:
        return
    tail(status["cmdline"][-1])
