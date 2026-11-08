from __future__ import annotations

import requests

from .auth import Credentials
from .basemanager import BaseManager
from .settings import get_base_url
from .utils import is_plural, singular


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
        self.session = session or requests.Session()
        self.extra_params = {"pagesize": "100"}
        self.name = singular(name) if is_plural(name) else name
        self.user_agent = user_agent or f"pyexo/{__version__} {requests.utils.default_user_agent()}"
