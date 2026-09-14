from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str
    price: int = Field(gt=0)
    description: str | None = None


# STEP4 自力課題 書籍更新用
class BookUpdate(BaseModel):
    title: str
    price: int = Field(gt=0)
    description: str | None = None
