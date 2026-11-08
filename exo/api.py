from __future__ import annotations

import requests

from .auth import Credentials
from .manager import Manager
from .settings import get_base_url


class Exo:
    """An ORM-like interface to the MYOB EXO API"""

    OBJECT_LIST: tuple[str, ...] = (
        "Activity",
        "ActivityStatus",
        "ActivityType",
        "BOM",
        "ComapanySearchTemplate",
        "CompanyDataFileInfo",
        "Contact",
        "CustomTable",
        "Debtor",
        "GeolocationSearchTemplate",
        "JobCategory",
        "JobFlagDescription",
        "JobProject",
        "JobStatus",
        "JobType",
        "Prospect",
        "Report",
        "SalesOrder",
        "SearchTemplate",
        "Stock",
        "StockClassification",
        "StockItem",
        "StockLocation",
        "StockPriceGroup",
        "StockPrimaryGroup",
        "StockSearchTemplate",
        "StockSecondaryGroup",
        "StockUnitOfMeasure",
        "Token",
    )

    def __init__(
        self,
        credentials: Credentials,
        base_url: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        """Iterate through the list of objects we support, for
        each of them create an attribute on our self that is
        the lowercase name of the object and attach it to an
        instance of a Manager object to operate on it.

        All managers share one ``requests.Session`` (connection reuse). Pass
        ``session`` to supply your own; otherwise one is created and closed by
        ``close()`` or by leaving a ``with`` block."""
        base_url = base_url or get_base_url()  # read .env once, not per manager
        self._owns_session = session is None
        self.session = session or requests.Session()
        for name in self.OBJECT_LIST:
            setattr(
                self,
                name.lower(),
                Manager(name, credentials, base_url=base_url, session=self.session),
            )

        self.listAPI = ExoList(credentials, base_url, self.session)

    def close(self) -> None:
        """Close the session, unless it was passed in (then it is yours to close)."""
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> Exo:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __getattr__(self, name: str) -> Manager:
        # Attributes are created dynamically from OBJECT_LIST (lowercase names).
        raise AttributeError(name)


class ExoList:
    """An ORM-like interface to the MYOB EXO List API"""

    OBJECT_LIST: tuple[str, ...] = (
        "AccountGroup",
        "AdvertType",
        "BasePrice",
        "Branch",
        "CommonPhrases",
        "CommunicationProcess",
        "Company",
        "CreditTerm",
        "Currency",
        "PaymentType",
        "Staff",
        "TaxRate",
    )

    def __init__(
        self,
        credentials: Credentials,
        base_url: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        base_url = base_url or get_base_url()
        for name in self.OBJECT_LIST:
            setattr(
                self,
                name.lower(),
                Manager(name, credentials, base_url=base_url, session=session),
            )

    def __getattr__(self, name: str) -> Manager:
        raise AttributeError(name)
