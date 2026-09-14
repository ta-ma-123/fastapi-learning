from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    description: str | None = None


class ProductUpdate(BaseModel):
    name: str
    price: int = Field(gt=0)
    description: str | None = None
