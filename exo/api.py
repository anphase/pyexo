from __future__ import annotations

from .auth import Credentials
from .manager import Manager


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

    def __init__(self, credentials: Credentials, base_url: str | None = None) -> None:
        """Iterate through the list of objects we support, for
        each of them create an attribute on our self that is
        the lowercase name of the object and attach it to an
        instance of a Manager object to operate on it"""
        for name in self.OBJECT_LIST:
            setattr(self, name.lower(), Manager(name, credentials, base_url=base_url))

        self.listAPI = ExoList(credentials, base_url)

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

    def __init__(self, credentials: Credentials, base_url: str | None = None) -> None:
        for name in self.OBJECT_LIST:
            setattr(self, name.lower(), Manager(name, credentials, base_url=base_url))

    def __getattr__(self, name: str) -> Manager:
        raise AttributeError(name)
