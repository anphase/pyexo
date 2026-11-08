"""Fetch one stock item by id: python get_stock_item.py 42"""

import sys

from exo import Exo
from exo.auth import Credentials
from exo.exceptions import ExoNotFound

exo = Exo(Credentials())

try:
    item = exo.stockitem.get(sys.argv[1])
except ExoNotFound:
    sys.exit(f"No stock item with id {sys.argv[1]}")

print(item["stockcode"], item["description"], item["sellprice"])
