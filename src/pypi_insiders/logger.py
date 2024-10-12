"""Logging utilities."""

from __future__ import annotations

import subprocess
import sys
import time
from contextlib import contextmanager
from io import StringIO
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Any, Callable

    from loguru import Record


def double_brackets(message: str) -> str:
    """Double `{` and `}` in log messages to prevent formatting errors.

    Parameters:
        message: The message to transform.

    Returns:
        The updated message.
    """
    return message.replace("{", "{{").replace("}", "}}")


def run(*args: str | Path, **kwargs: Any) -> str:
    """Run a subprocess, log its standard output and error, return its output.

    Parameters:
        *args: Command line arguments.
        **kwargs: Additional arguments passed to [subprocess.Popen][].

    Returns:
        The process standard output.
    """
    args_str = double_brackets(str(args))
    kwargs_str = double_brackets(str(kwargs))
    logger.debug(f"Running subprocess with args={args_str}, kwargs={kwargs_str}")
    process = subprocess.Popen(  # noqa: S603
        args,
        **kwargs,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = []
    while True:
        stdout_line = process.stdout.readline().strip()  # type: ignore[union-attr]
        stderr_line = process.stderr.readline().strip()  # type: ignore[union-attr]
        if stdout_line:
            logger.debug(f"STDOUT: {double_brackets(stdout_line)}", pkg=args[0])
            stdout.append(stdout_line)
        if stderr_line:
            logger.debug(f"STDERR: {double_brackets(stderr_line)}", pkg=args[0])
        if not stdout_line and not stderr_line:
            break
    process.wait()
    return "\n".join(stdout)


class _TextBuffer(StringIO):
    class _BytesBuffer:
        def __init__(self, text_buffer: _TextBuffer) -> None:
            self._text_buffer = text_buffer

        def flush(self) -> None: ...

        def write(self, value: bytes) -> int:
            return self._text_buffer.write(value.decode())

    def __init__(self, log_func: Callable[[str], None], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.log_func = log_func
        self.buffer = self._BytesBuffer(self)  # type: ignore[misc,assignment]

    def write(self, message: str) -> int:
        for line in message.split("\n"):
            if stripped := line.strip():
                self.log_func(stripped)
        return 0


@contextmanager
def redirect_output_to_logging(stdout_level: str = "info", stderr_level: str = "error") -> Iterator[None]:
    """Redirect standard output and error to logging.

    Yields:
        Nothing.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = _TextBuffer(getattr(logger, stdout_level))
    sys.stderr = _TextBuffer(getattr(logger, stderr_level))

    try:
        yield
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def log_captured(text: str, level: str = "info", pkg: str | None = None) -> None:
    """Log captured text.

    Parameters:
        text: The text to split and log.
        level: The log level to use.
    """
    log = getattr(logger, level)
    for line in text.splitlines(keepends=False):
        log(double_brackets(line), pkg=pkg)


def tail(log_file: str) -> None:
    """Tail a log file.

    Parameters:
        log_file: The log file to tail.
    """
    with open(log_file) as file:
        try:
            while True:
                line = file.readline()
                if line:
                    print(line, end="")  # noqa: T201
                else:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            return


def _update_record(record: Record) -> None:
    record["pkg"] = record["extra"].get("pkg") or (record["name"] or "").split(".", 1)[0]  # type: ignore[typeddict-unknown-key]


logger = logger.patch(_update_record)
