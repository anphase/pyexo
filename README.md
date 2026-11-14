PyExo
=====

PyExo is a Python API for accessing the REST API provided by the [MYOB EXO](http://developer.myob.com/api/exo) 
accounting tool. It allows access to local, remote and cloud applications.

## Quickstart:

Include the library folder with your application and import it.

### Authentication

All requests made to the MYOB EXO API require authentication headers that contain your EXO username, password, a 
developer key and an EXO token generated using the EXO Config application in your installation. You can find details 
for how to get these from the MYOB EXO Developer pages:[MYOB EXO API page](http://developer.myob.com/api/exo/exo-api-overview/authentication/).

#### Configuration

Credentials and the base URL are looked up in this order: arguments you pass in code, then environment
variables, then an optional `.env` file in the current directory.

<!-- slopcheck: allow IP_ENV (these variable names are the library's configuration interface) -->
| Setting  | Variable          |
| -------- | ----------------- |
| Username | `EXO_USERNAME`    |
| Password | `EXO_PASSWORD`    |
| API key  | `EXO_API_KEY`     |
| Token    | `EXO_TOKEN`       |
| Base URL | `EXO_BASE_URL`, or `EXO_IP` and `EXO_PORT` (builds `http://<ip>:<port>`) |

```shell script
$ export EXO_USERNAME=demo
$ export EXO_PASSWORD=DEMO
$ export EXO_API_KEY=ABCta353c5R6YXRvcjo=
$ export EXO_TOKEN='123AA353c5R6YXRsTAQ18*%'
$ export EXO_BASE_URL=http://192.168.0.1:8888
```

Or put the same names in a standard `KEY=VALUE` `.env` file (`#` comments, an optional `export ` prefix and
single or double quotes are understood):

```dotenv
EXO_BASE_URL=http://192.168.0.1:8888
EXO_USERNAME=demo
EXO_PASSWORD=DEMO
EXO_API_KEY=ABCta353c5R6YXRvcjo=
EXO_TOKEN=123AA353c5R6YXRsTAQ18*%
```

The INI-style `.env` with `[DEFAULT]` and `[AUTH]` sections used by 0.1 and 0.2 is still read, with a
`DeprecationWarning`, and will be removed in a later release. Convert it to the format above.

#### Setting the Authentication Headers

Setting the authentication headers is done when initialising an instance of the API. First import the modules:

```python
from exo import Exo
from exo.auth import Credentials
```

If you have the environment variables setup then:

```python
credentials = Credentials()
```

Otherwise you can enter them manually:

```python
credentials = Credentials(<username>, <passoword>, <key>, <token>)
```

Then pass them into an instance of the Exo class. Use it in a `with` block so the connection is closed
(or call `exo.close()`):

```python
with Exo(credentials) as exo:
    ...
```

`Exo()` with no arguments builds `Credentials()` and the base URL from the configuration above.

## Using the EXO API

The API is a work in progress, it returns dictionaries exactly as provided by the EXO API.

Responses are parsed JSON (dicts and lists), or `bytes` for non-JSON content such as PDF reports. Errors raise
subclasses of `exo.exceptions.ExoException` (`ExoNotFound`, `ExoUnauthorised`, ...), which keep the HTTP `response`.

Every EXO object is a lowercase attribute (`exo.debtor`, `exo.stockitem`, `exo.salesorder`), created on first use.
The List API objects work the same way and are also available as `exo.listAPI.currency`. A misspelt name raises
`AttributeError` with a suggestion. Use the singular object name; plural spellings passed to `Manager` still work
for now but emit a `DeprecationWarning`.

```python
exo.debtor.search("acme")
exo.stockitem.get(42)
exo.debtor.all({"page": 2})                   # one page (default page size 100)
for debtor in exo.debtor.iter_all():          # every page, until an empty one
    ...
exo.discovery()                               # GET <base>/discovery, parsed JSON
```

### Connections and retries

All managers of one `Exo` share a single `requests.Session`, so connections are reused. Pass your own with
`Exo(credentials, session=my_session)`; you then close it yourself.

pyexo's own request loop does all retrying, under one policy with one budget: responses 429, 502, 503 and 504,
connect errors and read errors (including a connection that drops while the body downloads) together are retried
up to 3 times, with exponential backoff that honours `Retry-After` (a wait longer than 60 seconds is clamped to 60).
Each retry waits for the timeout again, so one call can take several times `timeout`. `POST` is never retried after the
server may have received it, because the default policy only retries idempotent methods. Tune or disable it:

```python
Exo(credentials, retries=5, backoff_factor=1.0)
Exo(credentials, retries=0)                        # off
Exo(credentials, retries=urllib3.util.Retry(...))  # full control
```

A `Retry` is used as given, so its `total`, `connect`, `read`, `status`, `allowed_methods`, `status_forcelist` and
backoff settings all apply. If the session you pass in already has an adapter retry policy, that policy is used
and the adapter is switched to not retry on its own, so retries are never doubled.

The base URL defaults to the configuration above. For the cloud (LiveRelay) service pass it explicitly:
`Exo(credentials, base_url="https://exo.api.myob.com")`.

## Security notes

- Every request carries your username and password (HTTP Basic), developer key and token as headers.
  The on-premise EXO API is served over plain `http://`, so anything on the path between you and the
  server can read them: keep that traffic on a trusted network, or put TLS in front of the API and use an
  `https://` base URL. The cloud service is `https://` only.
- An `ExoException` keeps the `requests.Response`, and `response.request.headers` holds those same
  credentials. Log the exception message or `response.status_code`, not the whole response or request.
- `.env` is read from the current directory. Keep it out of version control (it is in `.gitignore`) and
  readable only by you.
- Ids passed to `get()` and `delete()` are percent-encoded (and an empty id, `.` or `..` is rejected), so an id from
  user input cannot change the request path or query.
- Redirects are not followed: a 3xx response raises `ExoExceptionUnknown` instead of re-sending your
  credentials to whatever host the `Location` header names.

## Examples

Short scripts in [`examples/`](examples/): [list debtors](examples/list_debtors.py),
[fetch a stock item](examples/get_stock_item.py) and [create a sales order](examples/create_sales_order.py).

## Development

```shell script
$ python -m venv .venv && .venv/bin/pip install -e '.[dev]'
$ scripts/check.sh   # ruff, mypy --strict, pytest with coverage
```

Tests run against mocked HTTP and hand-written fixtures; no EXO server is needed.

## Requirements
Python 3.11 or newer and the `requests` package.
