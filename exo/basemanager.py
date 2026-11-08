from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import requests

from .auth import Credentials
from .exceptions import (
    ExoBadRequest,
    ExoException,
    ExoExceptionUnknown,
    ExoForbidden,
    ExoInternalError,
    ExoNotFound,
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

    def iter_all(self, params: Params | None = None, page_size: int = 100) -> Iterator[Any]:
        """Yield every object, fetching pages until one comes back short or empty."""
        page = 1
        while True:
            items = self.all({**(params or {}), "page": page, "pagesize": page_size})
            yield from items
            if len(items) < page_size:
                return
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

        response = self.session.request(
            method, uri, data=body, headers=headers, params=params, timeout=self.timeout
        )

        if response.status_code in SUCCESS:
            if response.status_code == 204:
                return None
            # If we haven't got JSON, assume we're being returned a binary file
            if not response.headers.get("content-type", "").startswith("application/json"):
                return response.content
            return response.json()

        raise ERRORS.get(response.status_code, ExoExceptionUnknown)(response)
