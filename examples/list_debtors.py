"""List every debtor; iter_all fetches pages until an empty page is returned."""

from exo import Exo

# Reads EXO_* from the environment or .env; the with-block closes the connection.
with Exo() as exo:
    for debtor in exo.debtor.iter_all():
        print(debtor["id"], debtor["alphacode"], debtor["accountname"])
