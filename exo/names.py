"""The object names the EXO API exposes."""

from __future__ import annotations

OBJECTS: tuple[str, ...] = (
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

LIST_OBJECTS: tuple[str, ...] = (
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


def _plural_forms(name: str) -> tuple[str, ...]:
    forms = (name + "s", name + "es")
    return (*forms, name[:-1] + "ies") if name.endswith("y") else forms


# Deprecated plural spellings ("Debtors", "Activities") mapped to the singular name.
PLURALS: dict[str, str] = {
    plural: name for name in (*OBJECTS, *LIST_OBJECTS) for plural in _plural_forms(name)
}
