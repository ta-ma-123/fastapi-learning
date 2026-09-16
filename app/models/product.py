from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    # このModelが対応するDBテーブル名
    __tablename__ = "products"

    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True)

    # 商品名
    name: Mapped[str] = mapped_column(String(100))

    # 価格
    price: Mapped[int] = mapped_column()
