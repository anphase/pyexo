# Changelog

All notable changes to pyexo. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [semantic versioning](https://semver.org/).

## [0.2.0] - 2026-11-08

### Changed (breaking)
- Successful calls return parsed JSON (a `dict` or `list`), as the README always described. Before
  this release they returned a re-serialised JSON string.
- HTTP 408 raises `ExoTimeout` and HTTP 410 raises `ExoRemoved`. Both used to raise
  `ExoExceptionUnknown`.
- `import exo` no longer reads configuration. Missing credentials now raise when you create
  `Credentials()`, not at import time.
- The `Exo` constructor takes `credentials=` in place of `auth_headers=`.

### Added
- `pip install`-able packaging (`pyproject.toml`, Python 3.10 and later, `requests` as the only
  runtime dependency) and type hints throughout, with `py.typed`.
- `base_url` on `Exo` and `Manager`, so you can reach the cloud host (`https://exo.api.myob.com`)
  as well as a local `http://ip:port` server. `Manager` also takes a `timeout`.
- `from exo import Exo` now works.
- An offline test suite and three example scripts in `examples/`.

### Fixed
- The Basic authorisation header was malformed: it was built from a bytes repr (`Basic b'...'`).
- Search text is URL-encoded, so spaces and ampersands stay part of the search.
- Dictionary and list bodies are sent as JSON.
- Per-request `Accept` and `User-Agent` headers no longer leak into the shared credential headers.
- A response with no content type no longer raises `KeyError`.
- A `204 No Content` reply (for example after a delete) is a success, not an error.
- A `%` in a password or token in `.env` no longer breaks configuration parsing.
- The cache directory setting read the logs key.
- The README's environment variable names now match the ones the library reads.
