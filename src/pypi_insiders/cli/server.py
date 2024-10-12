"""CLI `server` command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pypi_insiders.server import server_logs, server_loop, server_status, start_server, stop_server

if TYPE_CHECKING:
    import argparse


def run_server_start(opts: argparse.Namespace) -> int:
    """Command to start the server in background.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    start_server(dist_dir=opts.dist_dir, port=opts.port)
    return 0


def run_server_status(opts: argparse.Namespace) -> int:
    """Command to show the server status.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    proc_data = server_status(port=opts.port)
    if proc_data:
        print("Running:")  # noqa: T201
        print(json.dumps(proc_data, indent=2, sort_keys=True))  # noqa: T201
    else:
        print("Not running")  # noqa: T201
    return 0


def run_server_stop(opts: argparse.Namespace) -> int:
    """Command to stop the server.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    return 0 if stop_server(port=opts.port) else 1


def run_server_run(opts: argparse.Namespace) -> int:
    """Command to run the server in foreground.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    server_loop(dist_dir=opts.dist_dir, port=opts.port)
    return 0


def run_server_logs(opts: argparse.Namespace) -> int:
    """Command to run the server in foreground.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    server_logs(port=opts.port)
    return 0


server_commands = {
    "start": run_server_start,
    "status": run_server_status,
    "stop": run_server_stop,
    "run": run_server_run,
    "logs": run_server_logs,
}


def run_server(opts: argparse.Namespace) -> int:
    """Command to manage the server.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    return server_commands.get(opts.server_subcommand, run_server_status)(opts)
