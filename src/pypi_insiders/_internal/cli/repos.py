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

from __future__ import annotations

from typing import TYPE_CHECKING

from pypi_insiders._internal.repos import RepositoryCache, RepositoryConfig

if TYPE_CHECKING:
    import argparse


def run_repos_add(opts: argparse.Namespace) -> int:
    """Command to add repositories.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    repos = RepositoryConfig(opts.conf_path)
    repos.add_repositories(dict(opts.repositories))
    return 0


def run_repos_list(opts: argparse.Namespace) -> int:
    """Command to list repositories.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    repos = RepositoryConfig(opts.conf_path)
    for repo, package_name in repos.get_repositories().items():
        print(f"{repo}: {package_name}")  # noqa: T201
    return 0


def run_repos_remove(opts: argparse.Namespace) -> int:
    """Command to remove repositories.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    repos = RepositoryConfig(opts.conf_path)
    repos.remove_repositories(opts.repositories)
    cache = RepositoryCache(opts.repo_dir)
    for repo in opts.repositories:
        cache.remove(repo)
    return 0


repos_commands = {
    "add": run_repos_add,
    "list": run_repos_list,
    "remove": run_repos_remove,
}


def run_repos(opts: argparse.Namespace) -> int:
    """Command to manage repositories.

    Parameters:
        opts: The parsed CLI arguments.

    Returns:
        A CLI exit code.
    """
    return repos_commands.get(opts.repos_subcommand, run_repos_list)(opts)
