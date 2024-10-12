"""Logic for updating packages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

from pypi_insiders.defaults import DEFAULT_CONF_PATH, DEFAULT_INDEX_URL, DEFAULT_REPO_DIR
from pypi_insiders.logger import logger
from pypi_insiders.repos import RepositoryCache, RepositoryConfig
from pypi_insiders.server import DistCollection

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


def _normalize_version(version: str) -> str:
    if version[0] == "v":
        version = version[1:]
    return version.replace("+", ".").replace("-", ".")


def update_packages(
    *,
    conf_path: str | Path = DEFAULT_CONF_PATH,
    repo_dir: str | Path = DEFAULT_REPO_DIR,
    index_url: str = DEFAULT_INDEX_URL,
    repos: Iterable[str] | None = None,
) -> None:
    """Update PyPI packages.

    For each configured repository, pull latest contents,
    checkout latest tag, and if the corresponding version is not present on the index,
    build and upload distributions.

    Parameters:
        conf_path: The path to the configuration file.
        repo_dir: The directory containing the repository clones.
        index_url: The URL of the PyPI index to upload to.
        repos: Repositories to update. By default, all configured repositories are updated.
    """
    config = RepositoryConfig(conf_path)
    cache = RepositoryCache(repo_dir)
    dists = DistCollection(index_url)
    config_repos = config.get_repositories()
    repos = repos and list(repos) or []
    selected_repos = (
        {repo: package for repo, package in config_repos.items() if repo in repos} if repos else config_repos
    )

    for repo, pkg_name in selected_repos.items():
        if not cache.exists(repo):
            logger.info(f"{repo}: Cloning (git clone)")
            cache.clone(repo)
        else:
            logger.info(f"{repo}: Updating (git pull)")
            cache.checkout_origin_head(repo)
            cache.pull(repo)

        latest_tag = cache.latest_tag(repo)
        if latest_tag:
            logger.info(f"{repo}: Latest tag is {latest_tag}")
        else:
            logger.info(f"{repo}: No tags found")
            continue
        latest_version = dists.latest_version(pkg_name)
        if latest_version:
            logger.info(f"{repo}: Latest PyPI version is {latest_version}")

        normal_tag = _normalize_version(latest_tag)
        normal_version = _normalize_version(latest_version or "0.0.0")
        if latest_version is None or normal_tag != normal_version:
            try:
                if Version(normal_tag) < Version(normal_version):
                    logger.warning(f"Latest tag {latest_tag} is older than latest PyPI version {latest_version}")
                    if dists.version_exists(pkg_name, normal_tag):
                        continue
            except InvalidVersion:
                pass
            logger.info(f"{repo}: Building distributions")
            cache.remove_dist(repo)
            cache.checkout(repo, latest_tag)
            new_dists = cache.build(repo)
            logger.info(f"{repo}: Uploading distributions")
            dists.upload(new_dists)
            logger.success(f"{repo}: Built and published version {normal_tag}")
