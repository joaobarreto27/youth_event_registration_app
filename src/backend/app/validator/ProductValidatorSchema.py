from pydantic import BaseModel, PositiveFloat, NonNegativeFloat
from datetime import datetime


class ValidatorProductBase(BaseModel):
    product_name: str
    quantity: NonNegativeFloat
    price: PositiveFloat


class ValidatorProductCreate(ValidatorProductBase):
    pass


class ValidatorProductResponse(ValidatorProductBase):
    id_product: int
    product_name: str
    quantity: NonNegativeFloat
    price: PositiveFloat
    create_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True
