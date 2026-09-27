from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, comment="ID")
    title: Mapped[str] = mapped_column(String(100), comment="タイトル")
    explanation: Mapped[str | None] = mapped_column(String(1000), nullable=True, comment="説明")
    status: Mapped[bool] = mapped_column(default=False, comment="完了状態")
