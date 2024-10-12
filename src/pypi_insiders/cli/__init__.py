"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m pypi_insiders` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `pypi_insiders.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `pypi_insiders.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import logging
import sys
from functools import cache
from typing import TYPE_CHECKING

from pypi_insiders import debug
from pypi_insiders.cli.repos import run_repos
from pypi_insiders.cli.server import run_server
from pypi_insiders.cli.update import run_update
from pypi_insiders.cli.watcher import run_watcher
from pypi_insiders.defaults import (
    DEFAULT_CONF_PATH,
    DEFAULT_DIST_DIR,
    DEFAULT_INDEX_URL,
    DEFAULT_PORT,
    DEFAULT_REPO_DIR,
    DEFAULT_WATCHER_SLEEP,
)
from pypi_insiders.logger import logger

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

prog_name = "pypi-insiders"


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug.print_debug_info()
        sys.exit(0)


@cache
def _subparsers(parser: argparse.ArgumentParser) -> argparse._SubParsersAction:
    dest = "subcommand"
    parser_name = parser.prog.split(" ", 1)[-1].replace(" ", "_")
    if parser_name != prog_name:
        dest = f"{parser_name}_{dest}"
    return parser.add_subparsers(dest=dest, title="Commands", metavar=None, prog=prog_name)


def subparser(
    parser: argparse.ArgumentParser,
    command: str,
    command_help: str,
    help_option_text: str,
    **kwargs: Any,
) -> argparse.ArgumentParser:
    """Add a subparser to a parser.

    Parameters:
        parser: The parser to add the subparser to.
        command: The subcommand invoking this subparser.
        command_help: The subcommand description.
        help_option_text: The message of the subcommand's `-h` option.
        **kwargs: Additional parameters passed to `add_parser`.

    Returns:
        The subparser.
    """
    subparser = _subparsers(parser).add_parser(
        command,
        add_help=False,
        help=command_help,
        description=command_help,
        **kwargs,
    )
    subparser.add_argument("-h", "--help", action="help", help=help_option_text)
    return subparser


def add_arg_conf_path(parser: argparse.ArgumentParser) -> None:
    """Add a conf-path option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-c",
        "--conf-path",
        help="Repository configuration file path (default: %(default)s).",
        default=DEFAULT_CONF_PATH,
    )


def add_arg_log_level(parser: argparse.ArgumentParser) -> None:
    """Add a log-level option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-L",
        "--log-level",
        type=str.upper,
        choices=("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"),
        help="Log level to use when logging messages (default: %(default)s).",
        default="INFO",
    )


def add_arg_log_path(parser: argparse.ArgumentParser) -> None:
    """Add a log-path option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-P",
        "--log-path",
        help="Write log messages to this file path (default: stderr).",
        default=None,
    )


def add_arg_repositories_packages(parser: argparse.ArgumentParser) -> None:
    """Add a repository:package argument to the parser.

    Parameters:
        parser: The parser to add the option to.
    """

    def repo_pkg(arg: str) -> tuple[str, str]:
        try:
            repo, pkg = arg.split(":", 1)
        except ValueError as error:
            raise argparse.ArgumentTypeError("Repositories must be of the form NAMESPACE/PROJECT:PACKAGE") from error
        return repo, pkg

    parser.add_argument(
        "repositories",
        type=repo_pkg,
        nargs="+",
        help="List of NAMESPACE/PROJECT:PACKAGE repositories.",
    )


def add_arg_repositories(parser: argparse.ArgumentParser, nargs: str = "+") -> None:
    """Add a repository argument to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument("repositories", nargs=nargs, help="List of NAMESPACE/PROJECT repositories.")


def add_arg_dist_dir(parser: argparse.ArgumentParser) -> None:
    """Add a dist-dir option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-d",
        "--dist-dir",
        help="Directory where the distributions are stored (default: %(default)s).",
        default=DEFAULT_DIST_DIR,
    )


def add_arg_port(parser: argparse.ArgumentParser) -> None:
    """Add a port option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-p",
        "--port",
        help="Port on which to serve the PyPI server (default: %(default)s).",
        default=DEFAULT_PORT,
    )


def add_arg_repo_dir(parser: argparse.ArgumentParser) -> None:
    """Add a repo-dir option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-r",
        "--repo-dir",
        help="Directory where the repositories are cloned (default: %(default)s).",
        default=DEFAULT_REPO_DIR,
    )


def add_arg_index_url(parser: argparse.ArgumentParser) -> None:
    """Add an index-url option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-i",
        "--index-url",
        help="URL of the index to upload packages to (default: %(default)s).",
        default=DEFAULT_INDEX_URL,
    )


def add_arg_sleep(parser: argparse.ArgumentParser) -> None:
    """Add a sleep option to the parser.

    Parameters:
        parser: The parser to add the option to.
    """
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        help="Time to sleep in between iterations, in seconds (default: %(default)s).",
        default=DEFAULT_WATCHER_SLEEP,
    )


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    description = "Self-hosted PyPI server with automatic updates for Insiders versions of projects."
    parser = argparse.ArgumentParser(add_help=False, description=description, prog=prog_name)
    parser_with_commands_help = "Show this help message and exit. Commands also accept the -h/--help option."
    parser_without_commands_help = "Show this help message and exit."
    options = parser.add_argument_group(title="Global options")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {debug.get_version()}")
    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    options.add_argument("-h", "--help", action="help", help=parser_with_commands_help)

    repos = subparser(parser, "repos", "Manage insiders repositories.", parser_with_commands_help)
    repos_list = subparser(repos, "list", "List insiders repositories.", parser_without_commands_help)
    repos_add = subparser(repos, "add", "Add insiders repositories.", parser_without_commands_help)
    repos_remove = subparser(repos, "remove", "Remove insiders repositories.", parser_without_commands_help)

    update = subparser(parser, "update", "Update insiders packages.", parser_without_commands_help)

    server = subparser(parser, "server", "Manage local PyPI server.", parser_with_commands_help)
    server_start = subparser(server, "start", "Start local PyPI server in background.", parser_with_commands_help)
    server_status = subparser(server, "status", "See status of local PyPI server.", parser_with_commands_help)
    server_stop = subparser(server, "stop", "Stop local PyPI server.", parser_with_commands_help)
    server_run = subparser(server, "run", "Run local PyPI server in foreground.", parser_with_commands_help)
    server_logs = subparser(server, "logs", "Show local PyPI server logs.", parser_with_commands_help)

    watcher = subparser(parser, "watcher", "Manage repositories watcher.", parser_with_commands_help)
    watcher_start = subparser(
        watcher,
        "start",
        "Start repositories watcher in background.",
        parser_without_commands_help,
    )
    watcher_status = subparser(watcher, "status", "See status of repositories watcher.", parser_without_commands_help)
    watcher_stop = subparser(watcher, "stop", "Stop repositories watcher.", parser_without_commands_help)
    watcher_run = subparser(watcher, "run", "Run repositories watcher in foreground.", parser_without_commands_help)
    watcher_logs = subparser(watcher, "logs", "Show repositories watcher logs.", parser_without_commands_help)

    all_parsers = (
        parser,
        repos,
        repos_add,
        repos_list,
        repos_remove,
        update,
        server,
        server_start,
        server_stop,
        server_run,
        server_logs,
        watcher,
        watcher_start,
        watcher_status,
        watcher_stop,
        watcher_run,
        watcher_logs,
    )

    # add conf path option to all parsers
    for prsr in all_parsers:
        add_arg_conf_path(prsr)
        add_arg_log_level(prsr)
        add_arg_log_path(prsr)

    # add repositories option to repos add/remove
    add_arg_repositories_packages(repos_add)
    add_arg_repositories(repos_remove)
    add_arg_repo_dir(repos_remove)

    # add server options
    add_arg_dist_dir(server)
    add_arg_dist_dir(server_start)
    add_arg_dist_dir(server_run)
    add_arg_port(server)
    add_arg_port(server_start)
    add_arg_port(server_status)
    add_arg_port(server_stop)
    add_arg_port(server_run)

    # add update options
    add_arg_repo_dir(update)
    add_arg_index_url(update)
    add_arg_repositories(update, nargs="*")

    # add watcher options
    add_arg_repo_dir(watcher_start)
    add_arg_index_url(watcher_start)
    add_arg_sleep(watcher_start)
    add_arg_repo_dir(watcher_run)
    add_arg_index_url(watcher_run)
    add_arg_sleep(watcher_run)

    return parser


commands = {
    "repos": run_repos,
    "update": run_update,
    "server": run_server,
    "watcher": run_watcher,
}


class _InterceptHandler(logging.Handler):
    def __init__(self, level: int = 0, allow: str | tuple[str] | None = None) -> None:
        super().__init__(level)
        self.allow = allow

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Prevent too much noise from dependencies
        if self.allow and level == "INFO" and not record.name.startswith(self.allow):
            level = "DEBUG"

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        message = record.getMessage().replace("\n", " ")
        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


def configure_logging(level: str, path: str | Path | None = None, allow: str | tuple[str] | None = None) -> None:
    """Configure logging.

    Parameters:
        level: Log level (name).
        path: Log file path.
        allow: List of package names for which to allow log levels greater or equal to INFO level.
            Packages that are not allowed will see all their logs demoted to DEBUG level.
            If unspecified, allow everything.
    """
    sink = path or sys.stderr
    log_level = {
        "TRACE": logging.DEBUG - 5,  # 5
        "DEBUG": logging.DEBUG,  # 10
        "INFO": logging.INFO,  # 20
        "SUCCESS": logging.INFO + 5,  # 25
        "WARNING": logging.WARNING,  # 30
        "ERROR": logging.ERROR,  # 40
        "CRITICAL": logging.CRITICAL,  # 50
    }.get(level.upper(), logging.INFO)
    logging.basicConfig(handlers=[_InterceptHandler(allow=allow)], level=0, force=True)
    loguru_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | <cyan>{pkg}</cyan> - <level>{message}</level>"
    )
    logger.configure(handlers=[{"sink": sink, "level": log_level, "format": loguru_format}])


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `pypi-insiders` or `python -m pypi_insiders`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    configure_logging(opts.log_level, opts.log_path, allow="pypiserver")
    if not opts.subcommand:
        parser.print_usage(file=sys.stderr)
        return 1
    return commands[opts.subcommand](opts)
