from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MERCHANT = "merchant"
    CUSTOMER = "customer"

