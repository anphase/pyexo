"""The retry policy shared by a client's managers.

pyexo's own request loop (``BaseManager._send``) owns every retry: the session's
adapters never retry, so one ``urllib3`` ``Retry`` policy is the single budget for
connect errors, read errors (including a body that drops mid-download) and
retryable statuses.
"""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

RETRY_STATUSES = (429, 502, 503, 504)
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5
MAX_RETRY_AFTER = 60.0  # seconds; a larger Retry-After is clamped to this


def make_policy(
    retries: int | Retry | None = DEFAULT_RETRIES, backoff_factor: float = DEFAULT_BACKOFF
) -> Retry:
    """Return the retry policy for ``retries`` (a count, ``0``/``None`` for none, or a Retry).

    A count gives exponential backoff from ``backoff_factor`` seconds that honours
    ``Retry-After`` for 429, 502, 503 and 504. The default ``allowed_methods`` keep
    POST from being retried after the server may have received it. A ``Retry`` you
    pass is copied and used as is, so its ``total``, ``connect``, ``read``, ``status``,
    ``allowed_methods``, ``status_forcelist`` and backoff settings all apply.
    """
    if isinstance(retries, Retry):
        return retries.new()
    if retries:
        return Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=RETRY_STATUSES,
            respect_retry_after_header=True,
        )
    return Retry(0)


def resolve_policy(
    session: requests.Session | None,
    url: str,
    retries: int | Retry | None = DEFAULT_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF,
) -> Retry:
    """Pick the policy, taking over a ``session`` adapter's own retries if it has any.

    pyexo does the retrying, so an adapter policy found on a session you pass in is
    moved into the returned policy and the adapter is set to never retry; otherwise
    its retries would add to ours.
    """
    adapter = session.get_adapter(url) if session is not None else None
    if isinstance(adapter, HTTPAdapter):
        own = adapter.max_retries
        if own.total != 0 or own.read is not False:  # not requests' no-retry default
            adapter.max_retries = Retry(0, read=False)
            return own.new()
    return make_policy(retries, backoff_factor)
