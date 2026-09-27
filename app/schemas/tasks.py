from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    explanation: str | None = Field(default=None, max_length=1000)
    status: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    explanation: str | None = Field(default=None, max_length=1000)
    status: bool = False
