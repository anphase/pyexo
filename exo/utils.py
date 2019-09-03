OBJECT_NAMES = {
    "AccountGroups": "AccountGroup",
    "Activities": "Activity",
    "ActivityStatuses": "ActivityStatus",
    "ActivityTypes": "ActivityType",
    "AdvertTypes": "AdvertType",
    "BasePrices": "BasePrice",
    "BOMs": "BOM",
    "Branches": "Branch",
    "ComapanySearchTemplates": "ComapanySearchTemplate",
    "CommonPhrases": "CommonPhrases",
    "CommunicationProcesses": "CommunicationProcess",
    "Companies": "Company",
    "CompanyDataFileInfos": "CompanyDataFileInfo",
    "Contacts": "Contact",
    "CreditTerms": "CreditTerm",
    "Currencies": "Currency",
    "CustomTables": "CustomTable",
    "Debtors": "Debtor",
    "GeolocationSearchTemplates": "GeolocationSearchTemplate",
    "JobCategories": "JobCategory",
    "JobFlagDescriptions": "JobFlagDescription",
    "JobProjects": "JobProject",
    "JobStatuses": "JobStatus",
    "JobTypes": "JobType",
    "PaymentTypes": "PaymentType",
    "Prospects": "Prospect",
    "Reports": "Report",
    "SalesOrders": "SalesOrder",
    "SearchTemplates": "SearchTemplate",
    "Staffs": "Staff",
    "Stocks": "Stock",
    "StockClassifications": "StockClassification",
    "StockItems": "StockItem",
    "StockLocations": "StockLocation",
    "StockPriceGroups": "StockPriceGroup",
    "StockPrimaryGroups": "StockPrimaryGroup",
    "StockSearchTemplates": "StockSearchTemplate",
    "StockSecondaryGroups": "StockSecondaryGroup",
    "StockUnitOfMeasures": "StockUnitOfMeasure",
    "TaxRates": "TaxRate",
    "Tokens": "Token",
}


def is_plural(word):
    return word in OBJECT_NAMES.keys()


def singular(word):
    return OBJECT_NAMES.get(word)