import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from urllib3.util.retry import Retry

from exo import Exo
from exo.exceptions import ExoExceptionUnknown
from exo.session import make_session


class Handler(BaseHTTPRequestHandler):
    script: list[tuple[int, dict[str, str]]] = []
    seen: list[str] = []

    def _respond(self) -> None:
        type(self).seen.append(self.command)
        status, headers = type(self).script.pop(0) if type(self).script else (200, {})
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        body = b"[]"
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _respond

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def server():
    Handler.script, Handler.seen = [], []
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_transient_statuses_are_retried_until_success(credentials, server):
    Handler.script = [(429, {}), (502, {}), (503, {})]
    with Exo(credentials, base_url=server, backoff_factor=0) as exo:
        assert exo.debtor.all() == []
    assert len(Handler.seen) == 4


def test_retries_are_bounded_and_the_last_response_raises(credentials, server):
    Handler.script = [(503, {})] * 10
    with Exo(credentials, base_url=server, backoff_factor=0) as exo:
        with pytest.raises(ExoExceptionUnknown):
            exo.debtor.all()
    assert len(Handler.seen) == 4  # the first try plus three retries


def test_retry_after_is_honoured(credentials, server):
    Handler.script = [(429, {"Retry-After": "1"})]
    with Exo(credentials, base_url=server, backoff_factor=0) as exo:
        started = time.monotonic()
        exo.debtor.all()
    assert time.monotonic() - started >= 0.9


def test_retries_can_be_turned_off(credentials, server):
    Handler.script = [(503, {})]
    with Exo(credentials, base_url=server, retries=0) as exo:
        with pytest.raises(ExoExceptionUnknown):
            exo.debtor.all()
    assert len(Handler.seen) == 1


def test_posts_are_not_retried(credentials, server):
    Handler.script = [(503, {})]
    with Exo(credentials, base_url=server, backoff_factor=0) as exo:
        with pytest.raises(ExoExceptionUnknown):
            exo.salesorder.save({"a": 1})
    assert Handler.seen == ["POST"]


def test_a_retry_policy_can_be_passed():
    policy = Retry(total=7)
    session = make_session(policy)
    retry = session.get_adapter("https://exo.test").max_retries
    assert retry.total == 7 and retry.raise_on_status is False


def test_default_policy_covers_the_documented_statuses():
    retry = make_session().get_adapter("https://exo.test").max_retries
    assert retry.total == 3
    assert set(retry.status_forcelist) == {429, 502, 503, 504}
    assert retry.respect_retry_after_header


def test_retry_after_is_capped_at_sixty_seconds():
    from urllib3.response import HTTPResponse

    retry = make_session().get_adapter("https://exo.test").max_retries
    assert retry.get_retry_after(HTTPResponse(headers={"Retry-After": "3600"})) == 60
    assert retry.get_retry_after(HTTPResponse(headers={"Retry-After": "7"})) == 7
    assert retry.get_retry_after(HTTPResponse()) is None
