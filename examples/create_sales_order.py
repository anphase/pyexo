"""Validate, then create, a draft sales order for a debtor.

The field names below follow the EXO sales order resource; adjust them to your
installation. Validation does not save anything.
"""

from exo import Exo

order = {
    "debtorid": 1,
    "status": 0,  # 0 = draft
    "lines": [{"stockcode": "WIDGET-1", "orderquantity": 2}],
}

with Exo() as exo:
    validated_order = exo.salesorder.save(order, validate=True)
    print(exo.salesorder.save(validated_order))
