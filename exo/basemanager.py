from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import Credentials
from .exceptions import (
    ExoBadRequest,
    ExoException,
    ExoExceptionUnknown,
    ExoForbidden,
    ExoInternalError,
    ExoNotFound,
    ExoPaginationError,
    ExoRemoved,
    ExoTimeout,
    ExoUnauthorised,
)

Params = dict[str, Any]
Body = dict[str, Any] | list[Any] | str | bytes | None

ERRORS: dict[int, type[ExoException]] = {
    400: ExoBadRequest,
    401: ExoUnauthorised,
    403: ExoForbidden,
    404: ExoNotFound,
    408: ExoTimeout,
    410: ExoRemoved,
    500: ExoInternalError,
}
SUCCESS = (200, 201, 202, 204)
BODY_RETRY_METHODS = ("get", "put", "delete")  # never POST: it could be applied twice
BODY_ERRORS = (
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.ConnectionError,
    requests.exceptions.ReadTimeout,
)


class BaseManager:
    """HTTP plumbing shared by all managers."""

    credentials: Credentials
    base_url: str
    name: str
    user_agent: str
    timeout: float
    session: requests.Session
    extra_params: Params

    def _url(self, *parts: str) -> str:
        return "/".join([self.base_url, self.name, *parts])

    def _merged(self, params: Params | None) -> Params:
        return {**self.extra_params, **(params or {})}

    def all(self, params: Params | None = None) -> Any:
        """List objects; pass ``{"page": n}`` etc. to page through results."""
        return self._request("get", self._url(), self._merged(params))

    def iter_all(
        self, params: Params | None = None, page_size: int = 100, max_pages: int | None = None
    ) -> Iterator[Any]:
        """Yield every object, fetching pages until one comes back empty.

        A server may return fewer than ``page_size`` items per page, so only an empty
        page ends the iteration. Raises ``ExoPaginationError`` if a page repeats the
        previous one (an endpoint that ignores ``page``) or if ``max_pages`` pages have
        been fetched and more remain.
        """
        previous: Any = None
        page = 1
        while True:
            items = self.all({**(params or {}), "page": page, "pagesize": page_size})
            if not items:
                return
            if max_pages is not None and page > max_pages:
                raise ExoPaginationError(f"more than max_pages={max_pages} pages of {self.name}")
            if items == previous:
                raise ExoPaginationError(
                    f"{self.name} returned page {page} twice; it may ignore paging"
                )
            yield from items
            previous = items
            page += 1

    def get(self, id: str | int, params: Params | None = None) -> Any:
        return self._request("get", self._url(str(id)), self._merged(params))

    def search(self, search_params: str, params: Params | None = None) -> Any:
        return self._request(
            "get", self._url("search"), self._merged({"q": search_params, **(params or {})})
        )

    def delete(self, id: str | int) -> Any:
        return self._request("delete", self._url(str(id)))

    def put(self, data: Body, validate: bool = False) -> Any:
        return self._write("put", data, validate)

    def save(self, data: Body, validate: bool = False) -> Any:
        return self._write("post", data, validate)

    def _write(self, method: str, data: Body, validate: bool) -> Any:
        parts = ("validate",) if validate else ()
        return self._request(method, self._url(*parts), self._merged(None), data)

    def _request(
        self, method: str, uri: str, params: Params | None = None, body: Body = None
    ) -> Any:
        # Copy so per-request headers never leak into the shared credentials.
        headers = dict(self.credentials.auth_headers)
        # Default to JSON, but a caller may want a PDF (application/pdf).
        headers.setdefault("Accept", "application/json")
        headers["User-Agent"] = self.user_agent
        if body is not None and not isinstance(body, str | bytes):
            body = json.dumps(body)
            headers["Content-Type"] = "application/json"

        response = self._send(method, uri, body, headers, params)

        if response.status_code in SUCCESS:
            if response.status_code == 204:
                return None
            # If we haven't got JSON, assume we're being returned a binary file
            if not response.headers.get("content-type", "").startswith("application/json"):
                return response.content
            return response.json()

        raise ERRORS.get(response.status_code, ExoExceptionUnknown)(response)

    def _send(
        self, method: str, uri: str, body: Body, headers: dict[str, str], params: Params | None
    ) -> requests.Response:
        """Send the request and read the whole body, retrying a failed body download.

        requests reads the body outside urllib3's retry loop, so a connection that drops
        after the headers arrive would otherwise fail on the first attempt. The retry
        count and backoff come from the session adapter's ``Retry`` policy; POST is
        never retried.
        """
        adapter = self.session.get_adapter(uri)
        policy = adapter.max_retries if isinstance(adapter, HTTPAdapter) else Retry(0)
        retries = int(policy.total or 0) if method.lower() in BODY_RETRY_METHODS else 0
        attempt = 0
        while True:
            response = self.session.request(
                method,
                uri,
                data=body,
                headers=headers,
                params=params,
                timeout=self.timeout,
                stream=True,
            )
            try:
                response.content  # noqa: B018 - read now so a failure is caught here
            except BODY_ERRORS:
                response.close()
                if attempt >= retries:
                    raise
                attempt += 1
                # Same schedule as urllib3: no wait before the first retry, then doubling.
                if attempt > 1:
                    time.sleep(min(policy.backoff_max, policy.backoff_factor * 2 ** (attempt - 1)))
                continue
            return response
