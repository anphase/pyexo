from .manager import Manager


class Exo(object):
    """An ORM-like interface to the MYOB EXO API"""

    OBJECT_LIST = (
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

    def __init__(self, auth_headers):
        """Iterate through the list of objects we support, for
        each of them create an attribute on our self that is
        the lowercase name of the object and attach it to an
        instance of a Manager object to operate on it"""
        for name in self.OBJECT_LIST:
            setattr(self, name.lower(), Manager(name, auth_headers))

        setattr(self, "listAPI", ExoList(auth_headers))


class ExoList(object):
    """An ORM-like interface to the MYOB EXO List API"""

    OBJECT_LIST = (
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

    def __init__(self, auth_headers):
        for name in self.OBJECT_LIST:
            setattr(self, name.lower(), Manager(name, auth_headers))
