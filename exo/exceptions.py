from __future__ import annotations

from collections.abc import Sequence

import requests


class ExoException(Exception):
    def __init__(self, response: requests.Response | None, msg: str | None = None) -> None:
        self.response = response
        super().__init__(msg)


class _HttpError(ExoException):
    def __init__(self, response: requests.Response) -> None:
        super().__init__(response, response.text)


class ExoBadRequest(_HttpError):
    """HTTP 400: Bad Request"""


class ExoUnauthorised(_HttpError):
    """HTTP 401: Unauthorised"""


class ExoForbidden(_HttpError):
    """HTTP 403: Forbidden"""


class ExoNotFound(_HttpError):
    """HTTP 404: Resource Not Found"""


class ExoTimeout(_HttpError):
    """HTTP 408: Timeout"""


class ExoRemoved(_HttpError):
    """HTTP 410: Resource Removed"""


class ExoInternalError(_HttpError):
    """HTTP 500: Internal Error"""


class ExoExceptionUnknown(_HttpError):
    """Any other unsuccessful HTTP status"""


class ExoIncompleteAuthorisation(ExoException):
    """Incomplete authorisation data"""

    def __init__(self, missing: Sequence[str] = ()) -> None:
        detail = f" (missing: {', '.join(missing)})" if missing else ""
        super().__init__(
            None,
            "Incomplete EXO authorisation" + detail + ". Set EXO_USERNAME, EXO_PASSWORD, "
            "EXO_API_KEY and EXO_TOKEN as environment variables or in the [AUTH] section "
            "of a .env file.",
        )
