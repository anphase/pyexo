import json

import pytest
import requests
import responses

from exo import Exo
from exo.manager import Manager

from .conftest import load_fixture


@responses.activate
def test_all_builds_url_and_sends_default_pagination(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=load_fixture("debtor_list.json"))
    result = Manager("Debtor", credentials, base_url=base_url).all()
    assert [(d["id"], d["alphacode"], d["accountname"]) for d in result] == [
        (1, "TEST001", "Example Trading Pty Ltd"),
        (2, "TEST002", "Sample Supplies Ltd"),
    ]
    request = responses.calls[0].request
    assert request.url == f"{base_url}/Debtor?pagesize=100"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["x-myobapi-key"] == "key-123"
    assert request.headers["User-Agent"].startswith("pyexo/")


@responses.activate
def test_all_merges_and_overrides_params(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[])
    Manager("Debtor", credentials, base_url=base_url).all({"page": 2, "pagesize": 10})
    url = responses.calls[0].request.url
    assert "page=2" in url and "pagesize=10" in url and "pagesize=100" not in url


@responses.activate
def test_get_fetches_single_object(credentials, base_url):
    responses.get(f"{base_url}/StockItem/WIDGET-1", json=load_fixture("stockitem.json"))
    item = Manager("StockItem", credentials, base_url=base_url).get("WIDGET-1")
    assert item["id"] == "WIDGET-1"
    assert [price["price"] for price in item["saleprices"]] == [9.95, 8.5]


@responses.activate
def test_search_url_encodes_the_query(credentials, base_url):
    responses.get(f"{base_url}/Debtor/search", json=[])
    Manager("Debtor", credentials, base_url=base_url).search("accountname like A&B co")
    url = responses.calls[0].request.url
    assert url.startswith(f"{base_url}/Debtor/search?")
    assert "q=accountname+like+A%26B+co" in url or "q=accountname%20like%20A%26B%20co" in url
    assert url.count("?") == 1


@responses.activate
def test_plural_names_are_singularised(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[])
    Manager("Debtors", credentials, base_url=base_url).all()
    assert responses.calls[0].request.url.startswith(f"{base_url}/Debtor?")


@responses.activate
def test_delete(credentials, base_url):
    responses.delete(f"{base_url}/SalesOrder/7", json={})
    Manager("SalesOrder", credentials, base_url=base_url).delete(7)
    assert responses.calls[0].request.url == f"{base_url}/SalesOrder/7"


@responses.activate
def test_save_posts_json_body(credentials, base_url):
    responses.post(f"{base_url}/SalesOrder", json={"id": 1}, status=201)
    payload = {"debtorid": 1, "status": 0}
    Manager("SalesOrder", credentials, base_url=base_url).save(payload)
    request = responses.calls[0].request
    assert json.loads(request.body) == payload
    assert request.headers["Content-Type"] == "application/json"


@responses.activate
def test_put_with_validate(credentials, base_url):
    responses.put(f"{base_url}/SalesOrder/validate", json={})
    Manager("SalesOrder", credentials, base_url=base_url).put({"id": 1}, validate=True)
    assert responses.calls[0].request.url.startswith(f"{base_url}/SalesOrder/validate")


@responses.activate
def test_string_body_is_sent_unchanged(credentials, base_url):
    responses.post(f"{base_url}/SalesOrder", json={})
    Manager("SalesOrder", credentials, base_url=base_url).save('{"a": 1}')
    assert responses.calls[0].request.body == '{"a": 1}'


@responses.activate
def test_binary_responses_are_returned_as_bytes(credentials, base_url):
    responses.get(f"{base_url}/Report/1", body=b"%PDF-1.4", content_type="application/pdf")
    assert Manager("Report", credentials, base_url=base_url).get(1) == b"%PDF-1.4"


@responses.activate
def test_request_does_not_mutate_credentials_headers(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[])
    Manager("Debtor", credentials, base_url=base_url).all()
    assert "Accept" not in credentials.auth_headers
    assert "User-Agent" not in credentials.auth_headers


@responses.activate
def test_custom_user_agent(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[])
    Manager("Debtor", credentials, user_agent="mine/1", base_url=base_url).all()
    assert responses.calls[0].request.headers["User-Agent"] == "mine/1"


@responses.activate
def test_exo_exposes_a_manager_per_object(credentials, base_url):
    exo = Exo(credentials, base_url=base_url)
    responses.get(f"{base_url}/StockItem/WIDGET-1", json=load_fixture("stockitem.json"))
    responses.get(f"{base_url}/Currency", json=[])
    assert exo.stockitem.get("WIDGET-1")["id"] == "WIDGET-1"
    exo.listAPI.currency.all()
    assert isinstance(exo.debtor, Manager)


def test_default_base_url_comes_from_settings(credentials, monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("[DEFAULT]\nEXO_IP = 10.1.1.1\nEXO_PORT = 1\n")
    monkeypatch.chdir(tmp_path)
    assert Manager("Debtor", credentials).base_url == "http://10.1.1.1:1"


def test_unknown_names_are_kept_as_given(credentials, base_url):
    assert Manager("Debtor", credentials, base_url=base_url).name == "Debtor"
    with pytest.raises(ValueError):
        Manager("", credentials, base_url=base_url)


def test_unknown_attributes_raise(credentials, base_url):
    exo = Exo(credentials, base_url=base_url)
    with pytest.raises(AttributeError):
        exo.nonsense  # noqa: B018
    with pytest.raises(AttributeError):
        exo.listAPI.nonsense  # noqa: B018


def test_exo_managers_share_one_session(credentials, base_url):
    exo = Exo(credentials, base_url=base_url)
    assert exo.debtor.session is exo.stockitem.session is exo.listAPI.currency.session
    assert exo.session is exo.debtor.session


def test_exo_accepts_a_session_and_leaves_it_open(credentials, base_url):
    session = requests.Session()
    closed = []
    session.close = lambda: closed.append(True)  # type: ignore[method-assign]
    with Exo(credentials, base_url=base_url, session=session) as exo:
        assert exo.debtor.session is session
    assert closed == []


def test_exo_closes_its_own_session(credentials, base_url):
    closed = []
    with Exo(credentials, base_url=base_url) as exo:
        exo.session.close = lambda: closed.append(True)  # type: ignore[method-assign]
    assert closed == [True]


@responses.activate
def test_iter_all_follows_pages_until_a_short_page(credentials, base_url):
    pages = {"1": [{"id": 1}, {"id": 2}], "2": [{"id": 3}, {"id": 4}], "3": [{"id": 5}]}
    responses.add_callback(
        responses.GET,
        f"{base_url}/Debtor",
        callback=lambda req: (
            200,
            {"Content-Type": "application/json"},
            json.dumps(pages[req.params["page"]]),
        ),
    )
    manager = Manager("Debtor", credentials, base_url=base_url)
    assert [d["id"] for d in manager.iter_all(page_size=2)] == [1, 2, 3, 4, 5]
    assert all(call.request.params["pagesize"] == "2" for call in responses.calls)


@responses.activate
def test_iter_all_stops_on_an_empty_page_and_keeps_params(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[{"id": 1}])
    responses.get(f"{base_url}/Debtor", json=[])
    manager = Manager("Debtor", credentials, base_url=base_url)
    assert [d["id"] for d in manager.iter_all({"filter": "x"}, page_size=1)] == [1]
    assert len(responses.calls) == 2
    assert responses.calls[0].request.params["filter"] == "x"


@responses.activate
def test_all_is_still_a_single_page(credentials, base_url):
    responses.get(f"{base_url}/Debtor", json=[{"id": 1}] * 100)
    assert len(Manager("Debtor", credentials, base_url=base_url).all()) == 100
    assert len(responses.calls) == 1
