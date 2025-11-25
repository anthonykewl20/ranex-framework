from datetime import datetime
from pydantic import BaseModel, Field


# Pydantic Schemas for API
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    sku: str = Field(..., min_length=1, max_length=100)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    sku: str | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

