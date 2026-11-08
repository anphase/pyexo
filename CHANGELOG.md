# Changelog

All notable changes to pyexo. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [semantic versioning](https://semver.org/).

## [0.3.0] - 2026-11-08

### Changed (breaking)
- Python 3.11 or newer is required (3.10 reached end of life in October 2026).
- `Exo` and `ExoList` are one class. `ExoList` is gone from `exo`; `exo.listAPI.currency` still works,
  and List API objects are also reachable directly (`exo.currency`). Managers are created on first
  access and cached, and an unknown name raises `AttributeError` with a close-match suggestion.
  `Exo.OBJECT_LIST` stays; the List API names are in `Exo.LIST_OBJECT_LIST`.
- `Exo` takes `credentials` and `base_url` as before, but everything after them is keyword-only, and
  `credentials` may be omitted (it then comes from the configuration).
- Configuration precedence is now constructor arguments, then environment variables, then `.env`.
  Previously a `.env` value beat the environment.
- The base URL can be set with `EXO_BASE_URL`; `EXO_IP` and `EXO_PORT` still work.
- Requests go through a per-client `requests.Session` and transient failures are retried by default
  (see Added), so a 429/502/503/504 that used to raise immediately may now succeed or take longer.

### Added
- `with Exo(...) as exo:` and `Exo.close()`; pass `session=` to supply your own `requests.Session`.
- Bounded retries (`retries=3`, `backoff_factor=0.5`) for 429, 502, 503 and 504 with exponential backoff
  and `Retry-After` (clamped to 60 seconds). `GET`, `PUT` and `DELETE` also retry connect and read errors;
  `POST` is never retried. Set `retries=0` to turn them off, or pass a `urllib3` `Retry`.
- `Manager.iter_all(params=None, page_size=100)` yields items across pages; `all()` is still one page.
- `Exo.discovery()` returns the parsed `GET <base>/discovery` response.
- Standard `KEY=VALUE` `.env` files (comments, `export`, quotes), and `EXO_BASE_URL`.
- `exo.timeout` and `user_agent` arguments on `Exo`, passed to its managers.

### Deprecated
- Plural object names given to `Manager` (`"Debtors"`, `"Activities"`) emit `DeprecationWarning`; use the
  singular name.
- The INI-style `.env` (`[DEFAULT]` and `[AUTH]` sections) still works for this release but emits
  `DeprecationWarning`.

### Removed
- `exo.utils` (the plural-name table), `ExoList`, and the unused `get_logs_directory` and
  `get_cache_directory` settings functions.

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
