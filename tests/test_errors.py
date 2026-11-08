import pytest
import requests
import responses

from exo import exceptions as exc
from exo.manager import Manager

from .conftest import load_fixture


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (400, exc.ExoBadRequest),
        (401, exc.ExoUnauthorised),
        (403, exc.ExoForbidden),
        (404, exc.ExoNotFound),
        (408, exc.ExoTimeout),
        (410, exc.ExoRemoved),
        (500, exc.ExoInternalError),
        (418, exc.ExoExceptionUnknown),
        (503, exc.ExoExceptionUnknown),
    ],
)
@responses.activate
def test_status_codes_map_to_exceptions(status, error, credentials, base_url):
    responses.get(f"{base_url}/Debtor/1", json=load_fixture("error_body.json"), status=status)
    with pytest.raises(error) as info:
        Manager("Debtor", credentials, base_url=base_url).get(1)
    assert info.value.response.status_code == status
    assert "Example error from a fixture" in str(info.value)
    assert isinstance(info.value, exc.ExoException)


@pytest.mark.parametrize("status", [200, 201, 202])
@responses.activate
def test_success_statuses(status, credentials, base_url):
    responses.get(f"{base_url}/Debtor/1", json={"id": 1}, status=status)
    assert Manager("Debtor", credentials, base_url=base_url).get(1) == {"id": 1}


@responses.activate
def test_network_timeout_propagates(credentials, base_url):
    responses.get(f"{base_url}/Debtor/1", body=requests.exceptions.ConnectTimeout())
    with pytest.raises(requests.exceptions.ConnectTimeout):
        Manager("Debtor", credentials, base_url=base_url).get(1)


def test_incomplete_authorisation_has_no_response():
    error = exc.ExoIncompleteAuthorisation()
    assert error.response is None
    assert "EXO_USERNAME" in str(error)


@responses.activate
def test_no_content_returns_none(credentials, base_url):
    responses.delete(f"{base_url}/SalesOrder/7", status=204)
    assert Manager("SalesOrder", credentials, base_url=base_url).delete(7) is None
