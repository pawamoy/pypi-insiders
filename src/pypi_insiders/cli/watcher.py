"""CLI `watcher` command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pypi_insiders.watcher import start_watcher, stop_watcher, watcher_logs, watcher_loop, watcher_status

if TYPE_CHECKING:
    import argparse


def run_watcher_start(opts: argparse.Namespace) -> int:
    """Command to start the watcher.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    start_watcher(
        conf_path=opts.conf_path,
        repo_dir=opts.repo_dir,
        index_url=opts.index_url,
        sleep=opts.sleep,
    )
    return 0


def run_watcher_status(opts: argparse.Namespace) -> int:  # noqa: ARG001
    """Command to show the watcher status.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    proc_data = watcher_status()
    if proc_data:
        print("Running:")  # noqa: T201
        print(json.dumps(proc_data, indent=2, sort_keys=True))  # noqa: T201
    else:
        print("Not running")  # noqa: T201
    return 0


def run_watcher_stop(opts: argparse.Namespace) -> int:  # noqa: ARG001
    """Command to stop the watcher.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    return 0 if stop_watcher() else 1


def run_watcher_run(opts: argparse.Namespace) -> int:
    """Command to run the watcher.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    watcher_loop(
        conf_path=opts.conf_path,
        repo_dir=opts.repo_dir,
        index_url=opts.index_url,
        sleep=opts.sleep,
    )
    return 0


def run_watcher_logs(opts: argparse.Namespace) -> int:  # noqa: ARG001
    """Command to show the watcher logs.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    watcher_logs()
    return 0


watcher_commands = {
    "start": run_watcher_start,
    "status": run_watcher_status,
    "stop": run_watcher_stop,
    "run": run_watcher_run,
    "logs": run_watcher_logs,
}


def run_watcher(opts: argparse.Namespace) -> int:
    """Command to manage the watcher.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    return watcher_commands.get(opts.watcher_subcommand, run_watcher_status)(opts)
