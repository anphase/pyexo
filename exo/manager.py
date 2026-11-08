from __future__ import annotations

import warnings

import requests

from .auth import Credentials
from .basemanager import BaseManager
from .names import KNOWN, PLURALS
from .session import make_session
from .settings import get_base_url


def _canonical(name: str) -> str:
    """Return the singular object name, warning if a deprecated plural was given."""
    if name not in KNOWN and name in PLURALS:
        warnings.warn(
            f"the plural name {name!r} is deprecated; use {PLURALS[name]!r}",
            DeprecationWarning,
            stacklevel=3,
        )
        return PLURALS[name]
    return name


def default_user_agent() -> str:
    from . import __version__

    return f"pyexo/{__version__} {requests.utils.default_user_agent()}"


class Manager(BaseManager):
    def __init__(
        self,
        name: str,
        credentials: Credentials,
        user_agent: str | None = None,
        base_url: str | None = None,
        timeout: float = 5,
        session: requests.Session | None = None,
    ) -> None:
        if not name:
            raise ValueError("name must not be empty")
        self.credentials = credentials
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.timeout = timeout
        self._owns_session = session is None
        self.session = session or make_session()
        self.extra_params = {"pagesize": "100"}
        self.name = _canonical(name)
        self.user_agent = user_agent or default_user_agent()

    def close(self) -> None:
        """Close the session if this manager created it; a session passed in is yours to close."""
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> Manager:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
