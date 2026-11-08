from __future__ import annotations

import base64

from .exceptions import ExoIncompleteAuthorisation
from .settings import AUTH_VARS, get_auth


class Credentials:
    """The three headers EXO requires on every request.

    Any argument left as None is read from the ``.env`` file or environment.
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        key: str | None = None,
        token: str | None = None,
    ) -> None:
        configured = get_auth()
        values = (
            username or configured["EXO_USERNAME"],
            password or configured["EXO_PASSWORD"],
            key or configured["EXO_API_KEY"],
            token or configured["EXO_TOKEN"],
        )
        missing = [name for name, value in zip(AUTH_VARS, values, strict=True) if not value]
        if missing:
            raise ExoIncompleteAuthorisation(missing)
        self._username, self._password, self._key, self._token = (str(v) for v in values)

        self.auth_headers: dict[str, str] = {
            "Authorization": self._basic_auth_code(self._username, self._password),
            "x-myobapi-key": self._key,
            "x-myobapi-exotoken": self._token,
        }

    @staticmethod
    def _basic_auth_code(username: str, password: str) -> str:
        auth_data = f"{username}:{password}"
        return "Basic " + base64.b64encode(auth_data.encode()).decode("ascii")
