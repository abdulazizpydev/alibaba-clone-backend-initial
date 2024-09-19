from enum import Enum, StrEnum


class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

    @classmethod
    def values(cls):
        return [choice.value for choice in cls]


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class GenderChoices(BaseEnum):
    MALE = "male"
    FEMALE = "female"


class UserRole(BaseEnum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class PolicyNameEnum(BaseEnum):
    BUYER_POLICY = "buyer_policy"
    SELLER_POLICY = "seller_policy"
    ADMIN_POLICY = "admin_policy"


class OrderStatus(BaseEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class PaymentProvider(BaseEnum):
    CLICK = 'click'
    PAYME = 'payme'
    CARD = 'card'
    PAYPAL = 'paypal'
