"""CLI `update` command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypi_insiders.update import update_packages

if TYPE_CHECKING:
    import argparse


def run_update(opts: argparse.Namespace) -> int:
    """Command to update packages.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    update_packages(conf_path=opts.conf_path, repo_dir=opts.repo_dir, index_url=opts.index_url, repos=opts.repositories)
    return 0
