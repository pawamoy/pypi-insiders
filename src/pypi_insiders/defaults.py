"""Default values throughout the project."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir

_APP_NAME = "pypi-insiders"
_APP_AUTHOR = _APP_NAME

DEFAULT_PORT = 31411
DEFAULT_INDEX_URL = f"http://localhost:{DEFAULT_PORT}"
DEFAULT_REPO_DIR = Path(user_cache_dir(_APP_NAME, _APP_AUTHOR))
DEFAULT_DIST_DIR = Path(user_data_dir(_APP_NAME, _APP_AUTHOR))
DEFAULT_CONF_DIR = Path(user_config_dir(_APP_NAME))
DEFAULT_CONF_PATH = DEFAULT_CONF_DIR / "repos.json"
DEFAULT_WATCHER_SLEEP = 30 * 60
