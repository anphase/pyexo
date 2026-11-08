import json
import runpy
from pathlib import Path

import pytest
import responses

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture(autouse=True)
def example_config(tmp_path):
    (tmp_path / ".env").write_text(
        "[DEFAULT]\nEXO_IP = exo.test\nEXO_PORT = 8888\n"
        "[AUTH]\nEXO_USERNAME = demo\nEXO_PASSWORD = secret\n"
        "EXO_API_KEY = key-123\nEXO_TOKEN = token-456\n"
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
