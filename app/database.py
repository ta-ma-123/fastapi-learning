from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# 設定クラスからDB接続先を取得する
engine = create_engine(settings.database_url)

# DB操作で使用するSessionを生成する
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
