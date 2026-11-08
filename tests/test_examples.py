import json
import runpy
import sys
from pathlib import Path

import pytest
import responses

from .conftest import load_fixture

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture(autouse=True)
def example_config(tmp_path):
    (tmp_path / ".env").write_text(
        "EXO_BASE_URL=http://exo.test:8888\nEXO_USERNAME=demo\nEXO_PASSWORD=secret\n"
        "EXO_API_KEY=key-123\nEXO_TOKEN=token-456\n"
    )


@responses.activate
def test_create_sales_order_submits_the_validation_response(base_url, capsys):
    validated_order = {
        "debtorid": 1,
        "status": 0,
        "lines": [{"stockcode": "WIDGET-1", "orderquantity": 2, "unitprice": 9.95}],
        "defaultlocationid": 1,
    }
    responses.post(f"{base_url}/SalesOrder/validate", json=validated_order)
    responses.post(f"{base_url}/SalesOrder", json={"id": 7}, status=201)

    runpy.run_path(str(EXAMPLES / "create_sales_order.py"), run_name="__main__")

    assert len(responses.calls) == 2
    validation_request, creation_request = [call.request for call in responses.calls]
    assert validation_request.url.startswith(f"{base_url}/SalesOrder/validate?")
    assert json.loads(validation_request.body) == {
        "debtorid": 1,
        "status": 0,
        "lines": [{"stockcode": "WIDGET-1", "orderquantity": 2}],
    }
    assert creation_request.url.startswith(f"{base_url}/SalesOrder?")
    assert json.loads(creation_request.body) == validated_order
    assert capsys.readouterr().out == "{'id': 7}\n"


@pytest.mark.parametrize(
    ("saleprices", "expected_prices"),
    [
        (load_fixture("stockitem.json")["saleprices"], "Retail 9.95\nTrade 8.5\n"),
        (None, ""),
        ([], ""),
    ],
)
@responses.activate
def test_get_stock_item_prints_code_and_available_prices(
    base_url, capsys, monkeypatch, saleprices, expected_prices
):
    item = load_fixture("stockitem.json")
    item["saleprices"] = saleprices
    responses.get(f"{base_url}/StockItem/WIDGET-1", json=item)
    monkeypatch.setattr(sys, "argv", ["get_stock_item.py", "WIDGET-1"])

    runpy.run_path(str(EXAMPLES / "get_stock_item.py"), run_name="__main__")

    assert capsys.readouterr().out == "WIDGET-1 Example widget\n" + expected_prices
    assert len(responses.calls) == 1


@responses.activate
def test_get_stock_item_reports_a_missing_code(base_url, monkeypatch):
    responses.get(f"{base_url}/StockItem/MISSING", status=404)
    monkeypatch.setattr(sys, "argv", ["get_stock_item.py", "MISSING"])

    with pytest.raises(SystemExit, match="No stock item with id MISSING"):
        runpy.run_path(str(EXAMPLES / "get_stock_item.py"), run_name="__main__")


@responses.activate
def test_list_debtors_prints_documented_fields_across_pages(base_url, capsys):
    debtors = load_fixture("debtor_list.json")
    responses.get(
        f"{base_url}/Debtor",
        json=debtors * 50,
        match=[responses.matchers.query_param_matcher({"page": "1", "pagesize": "100"})],
    )
    responses.get(
        f"{base_url}/Debtor",
        json=debtors,
        match=[responses.matchers.query_param_matcher({"page": "2", "pagesize": "100"})],
    )
    responses.get(
        f"{base_url}/Debtor",
        json=[],
        match=[responses.matchers.query_param_matcher({"page": "3", "pagesize": "100"})],
    )

    runpy.run_path(str(EXAMPLES / "list_debtors.py"), run_name="__main__")

    assert (
        capsys.readouterr().out
        == ("1 TEST001 Example Trading Pty Ltd\n2 TEST002 Sample Supplies Ltd\n") * 51
    )
    assert len(responses.calls) == 3
