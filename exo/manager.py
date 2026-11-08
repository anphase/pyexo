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
        from . import __version__

        if not name:
            raise ValueError("name must not be empty")
        self.credentials = credentials
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.timeout = timeout
        self.session = session or make_session()
        self.extra_params = {"pagesize": "100"}
        self.name = _canonical(name)
        self.user_agent = user_agent or f"pyexo/{__version__} {requests.utils.default_user_agent()}"
