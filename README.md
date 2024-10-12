# PyPI Insiders

[![ci](https://github.com/pawamoy/pypi-insiders/workflows/ci/badge.svg)](https://github.com/pawamoy/pypi-insiders/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://pawamoy.github.io/pypi-insiders/)
[![pypi version](https://img.shields.io/pypi/v/pypi-insiders.svg)](https://pypi.org/project/pypi-insiders/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-708FCC.svg?style=flat)](https://gitpod.io/#https://github.com/pawamoy/pypi-insiders)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#pypi-insiders:gitter.im)

Self-hosted PyPI server with automatic updates for Insiders versions of projects.

## Motivation

Some open source projects follow the **sponsorware release strategy**,
which means that new features are first exclusively released to sponsors
as part of an "Insiders" version of the project.
This Insiders version is usually a private fork of the public project.

To use the Insiders projects as dependencies, sponsors have two options:

1. specify the dependency as a Git URL (HTTPS or SSH), or as a direct HTTPS URL to a build artifact
1. build and store the artifact in a self-hosted PyPI-like index

The first option is problematic when sponsors' projects are also open source,
because most of their contributors will probably not have access to the Insiders version.
It means they won't be able to resolve the dependency, even less install it locally.
As a result, maintainers must specify the public version of the project as a dependency,
and override it with the Insiders version in Continuous Integration / Deployment.

In contrast, the second option allows maintainers to specify the dependency normally,
i.e. using the same name/identifier as the public version.
Maintainers/contributors with access to the Insiders version
will resolve and get the Insiders version,
while maintainers/contributors *without* access to the Insiders version
will simply get the public one.

However, self-hosting a PyPI-like index,
and building artifacts for each new Insiders version
is not a trivial, straight-forward task:
companies and organizations might already have such a setup
(with an [Artifactory] server, a [Google Cloud] registry, etc.),
but individual contributors often won't,
and automatically updating repositories, building artifacts
and uploading them requires custom scripts.

  [Artifactory]: https://jfrog.com/help/r/jfrog-artifactory-documentation/pypi-repositories
  [Google Cloud]: https://cloud.google.com/artifact-registry/docs/python

In both cases (company setup or individual contributor)
**PyPI Insiders** comes to the rescue, and manages repository/package updates for you.
It comes bundled with a PyPI-like index that you can serve locally,
and it watches Insiders repositories, building and uploading
distributions to your local index (or any other online index)
for each new Insiders version getting published.

See below how to install and use PyPI Insiders!

## Installation

```bash
pip install pypi-insiders
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install pypi-insiders
```

## Usage

Run the server with:

```bash
pypi-insiders server start
```

The local PyPI server should be running:

```bash
pypi-insiders server status
```

Now, if you wish, you can configure your tools to use your local index by default:

```bash
export PIP_INDEX_URL=http://localhost:31411/simple/
export PDM_PYPI_URL=http://localhost:31411/simple/
export UV_INDEX_URL=http://localhost:31411/simple/
```

Your local index will give precedence to its own packages,
and redirect to PyPI.org if it doesn't know the specified packages.
It means that Insiders versions will always take precedence
over public versions, even if the latter are higher (more recent).

Configuring your tools with environment variables makes it easy
to temporarily "deactivate" your local index:

```bash
# This will install directly from PyPI.org.
env -u PIP_INDEX_URL pip install something
env -u PDM_PYPI_URL pdm sync
env -u UV_INDEX_URL uv sync
```

You can declare a shell alias to make things even simpler:

```bash
alias no-insiders='env -u PIP_INDEX_URL -u PDM_PYPI_URL -u UV_INDEX_URL'
no-insiders uv sync
```

Configure the repositories to watch:

```bash
pypi-insiders repos add pawamoy-insiders/devboard:devboard
```

The format is `NAMESPACE/PROJECT:DISTRIBUTION_NAME`.
Only GitHub projects are supported for now.

List watched repositories:

```bash
pypi-insiders repos list
```

Remove watched repositories:

```bash
pypi-insiders repos remove pawamoy-insiders/devboard
```

Start/stop the local PyPI index, get the server status:

```bash
pypi-insiders server start
pypi-insiders server status
pypi-insiders server stop
```

Update all packages from watched repositories:

```bash
pypi-insiders update
```

Update a specific package:

```bash
pypi-insiders update pawamoy-insiders/devboard
```

Start/stop the watcher, get the watcher status:

```bash
pypi-insiders watcher start
pypi-insiders watcher status
pypi-insiders watcher stop
```

Show logs of the server/watcher:

```bash
pypi-insiders server logs
pypi-insiders watcher logs
```
