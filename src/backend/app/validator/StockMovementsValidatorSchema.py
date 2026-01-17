from pydantic import BaseModel, PositiveFloat, Field
from datetime import datetime
from typing import Optional


class ValidatorStockMovementBase(BaseModel):
    id_product: int
    quantity: PositiveFloat
    movement_type: str
    movement_date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ValidatorStockMovementCreate(ValidatorStockMovementBase):
    pass


class ValidatorStockMovementResponse(ValidatorStockMovementBase):
    id_product: int
    id_stock_movement: Optional[int] = None
    product_name: Optional[str] = None
    quantity: PositiveFloat
    movement_type: str

    class Config:
        from_attributes = True
