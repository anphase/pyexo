# EXO API notes

Checked against MYOB's public developer documentation (developer.myob.com/api/exo) in November 2026.

- The EXO API is still documented and offered for on-premise (local/remote) and cloud (LiveRelay) access. MYOB EXO Business has no announced end-of-life; the separate EXO Payroll suite is being retired and is not covered by this library.
- Every request needs three headers: `Authorization: Basic <base64(username:password)>`, `x-myobapi-key` (developer key) and `x-myobapi-exotoken` (token generated in EXO Config / EXO Business). Tokens expire with the API module licence (about a year).
- On-premise base URL: `http://<ip>:<port>`; cloud base URL: `https://exo.api.myob.com`. The documented entry point is `<base>/discovery`.

Differences found in this library (addressed on the `modernise` branch):

- The Basic credential was built with `str(bytes)`, producing `Basic b'...'` instead of the base64 text.
- Only plain `http://` on-premise URLs were supported; the cloud host was not.
- Settings were read (and required) at import time.

## Outlook

MYOB EXO Business and its REST API remain documented and supported, with no announced end-of-life. The developer pages are largely unchanged since about 2019, though, and MYOB has begun winding down the companion EXO Payroll suite, with consultancies publicly advising EXO customers to plan a move to MYOB Acumatica (previously MYOB Advanced) over the longer term. That successor is a different product with a different API (OAuth 2.0, different resources), so this library will keep targeting EXO as it stands today; a client for a successor API would be a separate piece of work rather than a rework of this one.
