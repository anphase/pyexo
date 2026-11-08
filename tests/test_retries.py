import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from exo import Exo
from exo.exceptions import ExoExceptionUnknown
from exo.session import make_policy, resolve_policy


class Handler(BaseHTTPRequestHandler):
    script: list[tuple[int, dict[str, str]]] = []
    seen: list[str] = []

    def _respond(self) -> None:
        type(self).seen.append(self.command)
        status, headers = type(self).script.pop(0) if type(self).script else (200, {})
        if headers.get("X-Truncate"):  # promise 10 bytes, send 3, drop the connection
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "10")
            self.end_headers()
            self.wfile.write(b"[1,")
            self.close_connection = True
            return
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        body = b"[]"
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_DELETE = _respond

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def server():
    Handler.script, Handler.seen = [], []
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


TRUNCATED = (200, {"X-Truncate": "1"})


def get(exo):
    return exo.debtor.all()


def test_transient_statuses_are_retried_until_success(credentials, server):
    Handler.script = [(429, {}), (502, {}), (503, {})]
    with Exo(credentials, base_url=server) as exo:
        assert get(exo) == []
    assert len(Handler.seen) == 4


def test_retries_are_bounded_and_the_last_response_raises(credentials, server):
    Handler.script = [(503, {})] * 10
    with Exo(credentials, base_url=server) as exo:
        with pytest.raises(ExoExceptionUnknown):
            get(exo)
    assert len(Handler.seen) == 4  # the first try plus three retries


def test_retry_after_is_honoured_and_capped_at_sixty_seconds(credentials, server, sleeps):
    Handler.script = [(429, {"Retry-After": "7"}), (503, {"Retry-After": "3600"})]
    with Exo(credentials, base_url=server) as exo:
        get(exo)
    assert sleeps == [7, 60]


def test_an_unparseable_retry_after_falls_back_to_the_backoff(credentials, server, sleeps):
    Handler.script = [(503, {"Retry-After": "soon"})]
    with Exo(credentials, base_url=server, backoff_factor=2) as exo:
        assert get(exo) == []
    assert len(Handler.seen) == 2
    assert sleeps == []  # urllib3 waits nothing before the first retry


def test_backoff_doubles_after_the_first_retry(credentials, server, sleeps):
    Handler.script = [(503, {})] * 3
    with Exo(credentials, base_url=server, backoff_factor=2) as exo:
        get(exo)
    assert sleeps == [4, 8]  # urllib3's schedule: no wait before the first retry


def test_retries_can_be_turned_off(credentials, server):
    Handler.script = [(503, {})]
    with Exo(credentials, base_url=server, retries=0) as exo:
        with pytest.raises(ExoExceptionUnknown):
            get(exo)
    assert len(Handler.seen) == 1


def test_posts_are_not_retried_on_a_status_or_a_dropped_body(credentials, server):
    with Exo(credentials, base_url=server) as exo:
        for script in ([(503, {})], [TRUNCATED]):
            Handler.script, Handler.seen = list(script), []
            with pytest.raises((ExoExceptionUnknown, requests.exceptions.RequestException)):
                exo.salesorder.save({"a": 1})
            assert Handler.seen == ["POST"]


@pytest.mark.parametrize("verb", ["all", "put", "delete"])
def test_a_body_that_drops_mid_download_is_retried(credentials, server, verb):
    Handler.script = [TRUNCATED, TRUNCATED]
    with Exo(credentials, base_url=server) as exo:
        args = {"all": (), "put": ({"a": 1},), "delete": (1,)}[verb]
        getattr(exo.debtor, verb)(*args)
    assert len(Handler.seen) == 3


def test_body_retries_are_bounded(credentials, server):
    Handler.script = [TRUNCATED] * 10
    with Exo(credentials, base_url=server) as exo:
        with pytest.raises(requests.exceptions.RequestException):
            get(exo)
    assert len(Handler.seen) == 4


def test_body_retries_can_be_turned_off(credentials, server):
    Handler.script = [TRUNCATED]
    with Exo(credentials, base_url=server, retries=0) as exo:
        with pytest.raises(requests.exceptions.RequestException):
            get(exo)
    assert len(Handler.seen) == 1


def test_one_budget_covers_statuses_and_dropped_bodies(credentials, server):
    # retries=1 must never turn into a status budget plus a separate body budget.
    Handler.script = [(503, {}), TRUNCATED, (503, {}), (200, {})]
    with Exo(credentials, base_url=server, retries=1) as exo:
        with pytest.raises(requests.exceptions.RequestException):
            get(exo)
    assert len(Handler.seen) == 2


@pytest.mark.parametrize("retries", [1, 2, 3])
def test_mixed_failures_never_exceed_the_budget(credentials, server, retries):
    Handler.script = [(503, {}), TRUNCATED, (429, {}), TRUNCATED, (504, {})] * 3
    with Exo(credentials, base_url=server, retries=retries) as exo:
        with pytest.raises((ExoExceptionUnknown, requests.exceptions.RequestException)):
            get(exo)
    assert len(Handler.seen) == retries + 1


def test_a_retry_with_read_zero_gives_no_body_retry(credentials, server):
    Handler.script = [TRUNCATED]
    with Exo(credentials, base_url=server, retries=Retry(total=2, read=0)) as exo:
        with pytest.raises(requests.exceptions.RequestException):
            get(exo)
    assert len(Handler.seen) == 1


def test_allowed_methods_gate_every_kind_of_retry(credentials, server):
    policy = Retry(total=3, status_forcelist=[503], allowed_methods={"PUT"})
    with Exo(credentials, base_url=server, retries=policy) as exo:
        for script in ([(503, {})], [TRUNCATED]):
            Handler.script, Handler.seen = list(script), []
            with pytest.raises((ExoExceptionUnknown, requests.exceptions.RequestException)):
                get(exo)
            assert len(Handler.seen) == 1
        Handler.script, Handler.seen = [TRUNCATED], []
        exo.debtor.put({"a": 1})
        assert len(Handler.seen) == 2


def test_a_retry_with_only_read_set_retries_the_body(credentials, server):
    Handler.script = [TRUNCATED, TRUNCATED]
    with Exo(credentials, base_url=server, retries=Retry(total=None, read=2)) as exo:
        assert get(exo) == []
    assert len(Handler.seen) == 3
    Handler.script, Handler.seen = [TRUNCATED] * 3, []
    with Exo(credentials, base_url=server, retries=Retry(total=None, read=2)) as exo:
        with pytest.raises(requests.exceptions.RequestException):
            get(exo)
    assert len(Handler.seen) == 3


def test_a_custom_retry_with_a_status_forcelist_ends_in_an_exo_error(credentials, server):
    Handler.script = [(503, {})] * 10
    policy = Retry(total=2, status_forcelist=[503])
    with Exo(credentials, base_url=server, retries=policy) as exo:
        with pytest.raises(ExoExceptionUnknown):
            get(exo)
    assert len(Handler.seen) == 3


def test_connect_errors_are_retried_then_raised(credentials, sleeps):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    with Exo(credentials, base_url=f"http://127.0.0.1:{port}", backoff_factor=1, retries=2) as exo:
        with pytest.raises(requests.exceptions.ConnectionError):
            get(exo)
    assert sleeps == [2]  # two retries: none before the first, then 1 * 2


def test_a_session_adapter_policy_is_taken_over(credentials, server):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=2, status_forcelist=[503]))
    session.mount("http://", adapter)
    Handler.script = [(503, {})] * 10
    with Exo(credentials, base_url=server, session=session) as exo:
        with pytest.raises(ExoExceptionUnknown):
            get(exo)
    assert len(Handler.seen) == 3  # the adapter itself no longer retries
    assert adapter.max_retries.total == 0


def test_a_plain_session_gets_the_default_policy():
    policy = resolve_policy(requests.Session(), "http://exo.test")
    assert policy.total == 3 and set(policy.status_forcelist) == {429, 502, 503, 504}
    assert policy.respect_retry_after_header


def test_policies_are_copied():
    original = Retry(total=7)
    assert make_policy(original) is not original
    assert make_policy(original).total == 7
    assert make_policy(0).total == 0 and make_policy(None).total == 0
