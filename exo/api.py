from __future__ import annotations

import difflib
from typing import Any

import requests
from urllib3.util.retry import Retry

from .auth import Credentials
from .manager import Manager, default_user_agent
from .names import LIST_OBJECTS, OBJECTS
from .session import DEFAULT_BACKOFF, DEFAULT_RETRIES, resolve_policy
from .settings import get_base_url

_LIST_KNOWN = {name.lower(): name for name in LIST_OBJECTS}
_KNOWN = {name.lower(): name for name in (*OBJECTS, *LIST_OBJECTS)}


def _suggest(name: str, known: dict[str, str], owner: str) -> AttributeError:
    message = f"{owner} has no object {name!r}"
    close = difflib.get_close_matches(name.lower(), known, n=1)
    if close:
        message += f"; did you mean {close[0]!r}?"
    return AttributeError(message)


class Exo:
    """An ORM-like interface to the MYOB EXO API.

    Every EXO object is a lowercase attribute (``exo.debtor``, ``exo.stockitem``)
    holding a :class:`Manager`, created the first time it is used and then cached.
    The List API objects are available the same way and also under ``exo.listAPI``
    (``exo.listAPI.currency``).

    All managers share one ``requests.Session`` for connection reuse. Pass
    ``session`` to supply your own; otherwise one is created and closed by
    ``close()`` or by leaving a ``with`` block.

    Retries are done by pyexo's own request loop under one ``urllib3`` ``Retry`` policy
    (``self.retry``): 429, 502, 503 and 504 responses, connect errors and read errors
    (including a body that drops mid-download) share a single budget of ``retries``
    (default 3) with exponential backoff and ``Retry-After`` (capped at 60 seconds).
    ``retries=0`` or ``None`` turns them off, and a ``Retry`` instance is used as is
    (``total``, ``connect``, ``read``, ``allowed_methods``, ``status_forcelist`` and
    backoff all apply). The default ``allowed_methods`` keep POST from being retried
    after the server may have received it. If the ``session`` you pass in has an adapter
    retry policy, it becomes the policy and the adapter is set to not retry itself.
    """

    OBJECT_LIST = OBJECTS
    LIST_OBJECT_LIST = LIST_OBJECTS

    def __init__(
        self,
        credentials: Credentials | None = None,
        base_url: str | None = None,
        *,
        session: requests.Session | None = None,
        retries: int | Retry | None = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF,
        timeout: float = 5,
        user_agent: str | None = None,
    ) -> None:
        self.credentials = credentials or Credentials()
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self._timeout = timeout
        self._user_agent = user_agent
        self._owns_session = session is None
        self.session = session or requests.Session()
        self._retry = resolve_policy(session, self.base_url, retries, backoff_factor)
        self._managers: dict[str, Manager] = {}

    @property
    def timeout(self) -> float:
        """Request timeout in seconds; changing it also updates managers already in use."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        self._timeout = value
        for manager in self._managers.values():
            manager.timeout = value

    @property
    def retry(self) -> Retry:
        """The ``Retry`` policy; changing it also updates managers already in use."""
        return self._retry

    @retry.setter
    def retry(self, value: Retry) -> None:
        self._retry = value
        for manager in self._managers.values():
            manager.retry = value

    @property
    def user_agent(self) -> str | None:
        """The User-Agent header (None for the default); changes reach managers in use."""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str | None) -> None:
        self._user_agent = value
        for manager in self._managers.values():
            manager.user_agent = value or default_user_agent()

    def _manager(self, name: str) -> Manager:
        if name not in self._managers:
            self._managers[name] = Manager(
                name,
                self.credentials,
                user_agent=self._user_agent,
                base_url=self.base_url,
                timeout=self._timeout,
                session=self.session,
                retries=self._retry,
            )
        return self._managers[name]

    def __getattr__(self, name: str) -> Manager:
        # Only reached when normal lookup fails. Underscore names never are objects,
        # and refusing them keeps copy/pickle from recursing before __init__ has run.
        if name.startswith("_") or name.lower() not in _KNOWN:
            raise _suggest(name, _KNOWN, "Exo")
        return self._manager(_KNOWN[name.lower()])

    def __dir__(self) -> list[str]:
        return sorted({*super().__dir__(), *_KNOWN})

    @property
    def listAPI(self) -> ListAPI:  # noqa: N802 - the public name since 0.1
        """The List API objects, as ``exo.listAPI.currency``."""
        return ListAPI(self)

    def discovery(self) -> Any:
        """Return the parsed JSON from ``GET <base>/discovery`` (what the server exposes)."""
        manager = self._manager("discovery")
        return manager._request("get", manager._url())

    def close(self) -> None:
        """Close the session, unless it was passed in (then it is yours to close)."""
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> Exo:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


class ListAPI:
    """A view of the List API objects on an :class:`Exo` client."""

    def __init__(self, exo: Exo) -> None:
        self._exo = exo

    def __getattr__(self, name: str) -> Manager:
        if name.startswith("_") or name.lower() not in _LIST_KNOWN:
            raise _suggest(name, _LIST_KNOWN, "listAPI")
        return self._exo._manager(_LIST_KNOWN[name.lower()])

    def __dir__(self) -> list[str]:
        return sorted({*super().__dir__(), *_LIST_KNOWN})
