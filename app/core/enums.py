from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MERCHANT = "merchant"
    CUSTOMER = "customer"

class CurrencyEnum(str, Enum):
    NGN = "NGN"
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"

class TransactionTypeEnum(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

