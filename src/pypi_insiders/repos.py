"""Manage repositories."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from build.__main__ import build_package
from failprint import Capture

from pypi_insiders.defaults import DEFAULT_CONF_PATH, DEFAULT_REPO_DIR
from pypi_insiders.logger import log_captured, run

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Any


class RepositoryConfig:
    """Repositories configuration."""

    def __init__(self, conf_path: str | Path = DEFAULT_CONF_PATH) -> None:
        """Initialize the instance.

        Parameters:
            conf_path: The path to the configuration file.
        """
        self.conf_path: Path = Path(conf_path)
        self.conf_path.parent.mkdir(exist_ok=True, parents=True)

    def get_repositories(self) -> dict[str, str]:
        """Get configured repositories.

        Returns:
            The dict of repositories (`"NAMESPACE/PROJECT": "PACKAGE"`).
        """
        try:
            with open(self.conf_path) as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_repositories(self, repos: dict[str, str]) -> dict[str, str]:
        """Save the given repositories into the configuration file.

        Parameters:
            repos: The repositories to save.

        Returns:
            The configured repositories.
        """
        with open(self.conf_path, "w") as file:
            json.dump(repos, file, indent=2)
        return repos

    def add_repositories(self, repos: dict[str, str]) -> dict[str, str]:
        """Add the given repositories to the configuration file.

        Parameters:
            repos: The repositories to add.

        Returns:
            The configured repositories.
        """
        config_repos = self.get_repositories()
        config_repos.update(repos)
        return self.save_repositories(config_repos)

    def remove_repositories(self, repos: Iterable[str]) -> dict[str, str]:
        """Remove the given repositories from the configuration file.

        Parameters:
            repos: The repositories to remove.

        Returns:
            The configured repositories.
        """
        repos = set(repos)
        config_repos = self.get_repositories()
        config_repos = {repo: pkg_name for repo, pkg_name in config_repos.items() if repo not in repos}
        return self.save_repositories(config_repos)


class RepositoryCache:
    """A cache for local clones of configured repositories."""

    def __init__(self, cache_dir: str | Path = DEFAULT_REPO_DIR) -> None:
        """Initialize the cache.

        Parameters:
            cache_dir: The directory in which to clone the repositories.
        """
        self.cache_dir: Path = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _git(self, repo: str, *args: str, **kwargs: Any) -> str:
        cached_repo = self.cache_dir / repo
        return run("git", "-C", cached_repo, *args, **kwargs)

    def exists(self, repo: str) -> bool:
        """Check if a repository already exists.

        Parameters:
            repo: The repository to check.

        Returns:
            True or false.
        """
        return self.cache_dir.joinpath(repo).exists()

    def clone(self, repo: str) -> Path:
        """Clone a repository.

        Parameters:
            repo: The repository to clone.

        Returns:
            The path to the cloned repository.
        """
        cached_repo = self.cache_dir / repo
        cached_repo.parent.mkdir(exist_ok=True)
        run("git", "clone", f"git@github.com:{repo}", cached_repo)
        return cached_repo

    def checkout(self, repo: str, ref: str) -> None:
        """Checkout a ref.

        Parameters:
            repo: The repository to work on.
        """
        self._git(repo, "checkout", ref)

    def checkout_origin_head(self, repo: str) -> None:
        """Checkout origin's HEAD again.

        Parameters:
            repo: The repository to work on.
        """
        self._git(repo, "remote", "set-head", "origin", "--auto")
        ref = self._git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
        self.checkout(repo, ref.strip().split("/")[3])

    def pull(self, repo: str) -> None:
        """Pull latest changes.

        Parameters:
            repo: The repository to work on.
        """
        self._git(repo, "pull")

    def latest_tag(self, repo: str) -> str:
        """Get the latest Git tag.

        Parameters:
            repo: The repository to work on.

        Returns:
            A tag.
        """
        return self._git(repo, "describe", "--tags", "--abbrev=0").strip()

    def remove(self, repo: str) -> None:
        """Remove a repository from the cache.

        Parameters:
            repo: The repository to remove.
        """
        shutil.rmtree(self.cache_dir / repo, ignore_errors=True)

    def remove_dist(self, repo: str) -> None:
        """Remove the `dist` folder of a repository.

        Parameters:
            repo: The repository to work on.
        """
        shutil.rmtree(self.cache_dir.joinpath(repo, "dist"), ignore_errors=True)

    def build(self, repo: str) -> Iterator[Path]:
        """Build distributions.

        Parameters:
            repo: The repository to work on.

        Returns:
            File path for each distribution.
        """
        cached_repo = self.cache_dir / repo
        with Capture.BOTH.here() as captured:
            build_package(cached_repo, cached_repo / "dist", distributions=["sdist", "wheel"])
        log_captured(str(captured), level="debug", pkg="build")
        return cached_repo.joinpath("dist").iterdir()
