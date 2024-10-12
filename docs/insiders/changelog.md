# Changelog

## PyPI Insiders Insiders

## 1.3.3 <small>February 19, 2024</small> { id="1.3.3" }

- Fix comparison of versions and tags with a `v` prefix (by ignoring the prefix)
- Enable fallback to PyPI.org

## 1.3.2 <small>January 04, 2024</small> { id="1.3.2" }

- Fix creation of configuration/cache directories (create parents too)

## 1.3.1 <small>October 20, 2023</small> { id="1.3.1" }

- Catch psutil errors to prevent crashes

## 1.3.0 <small>October 19, 2023</small> { id="1.3.0" }

- Expose function to configure logging
- Expose function to run a subprocess and log its output

## 1.2.5 <small>October 02, 2023</small> { id="1.2.5" }

- Always create dist directory

## 1.2.4 <small>September 21, 2023</small> { id="1.2.4" }

- Fix success log message (missing repository prefix)

## 1.2.3 <small>September 21, 2023</small> { id="1.2.3" }

- Double `{` and `}` brackets in log messages to prevent formatting errors

## 1.2.2 <small>September 17, 2023</small> { id="1.2.2" }

- Compare tag and version, check if exist to avoid building for nothing
- Fix passing log level on the command line
- Decrease watcher sleep time from 1 hour to 30 minutes

## 1.2.1 <small>August 20, 2023</small> { id="1.2.1" }

- Detect pre-releases when checking latest version on PyPI server
- Detect and use default Git branch

### 1.2.0 <small>August 17, 2023</small> { id="1.2.0" }

- Add commands to show server/watcher logs
- Improve logging

### 1.1.0 <small>June 13, 2023</small> { id="1.1.0" }

- Add logging options, improve logging
- Remove repository from cache as well as config
- Remove status from process metadata

### 1.0.0 <small>June 13, 2023</small> { id="1.0.0" }

- Release first Insiders version
