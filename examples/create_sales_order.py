"""Validate, then create, a draft sales order for a debtor.

The field names below follow the EXO sales order resource; adjust them to your
installation. Validation does not save anything.
"""

from exo import Exo
from exo.auth import Credentials

exo = Exo(Credentials())

order = {
    "debtorid": 1,
    "status": 0,  # 0 = draft
    "lines": [{"stockcode": "WIDGET-1", "quantity": 2}],
}

exo.salesorder.save(order, validate=True)
print(exo.salesorder.save(order))
