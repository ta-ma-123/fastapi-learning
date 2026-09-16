from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str
    price: int = Field(gt=0)
