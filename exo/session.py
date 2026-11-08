"""Construction of the ``requests.Session`` shared by a client's managers."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

RETRY_STATUSES = (429, 502, 503, 504)
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5


def make_session(
    retries: int | Retry | None = DEFAULT_RETRIES, backoff_factor: float = DEFAULT_BACKOFF
) -> requests.Session:
    """Return a session that retries 429, 502, 503 and 504 responses.

    ``retries`` is the number of retries (``0`` or ``None`` turns retrying off) or a
    ready-made ``urllib3.util.retry.Retry`` for full control. Waits grow exponentially
    from ``backoff_factor`` seconds, and a ``Retry-After`` header is honoured. Only
    idempotent methods are retried, so a ``POST`` is never sent twice.
    """
    session = requests.Session()
    if isinstance(retries, Retry):
        # Never raise RetryError: the last response goes through the ExoException mapping.
        policy: Retry = retries.new(raise_on_status=False)
    elif retries:
        policy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=RETRY_STATUSES,
            respect_retry_after_header=True,
            raise_on_status=False,  # hand the last response to the normal error mapping
        )
    else:
        return session
    adapter = HTTPAdapter(max_retries=policy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
