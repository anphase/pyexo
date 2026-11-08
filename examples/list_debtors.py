"""List debtors, following pagination until a short page is returned."""

from exo import Exo
from exo.auth import Credentials

exo = Exo(Credentials())  # reads EXO_* from the environment or .env

page = 1
while True:
    debtors = exo.debtor.all({"page": page, "pagesize": 100})
    for debtor in debtors:
        print(debtor["accountno"], debtor["name"])
    if len(debtors) < 100:
        break
    page += 1
