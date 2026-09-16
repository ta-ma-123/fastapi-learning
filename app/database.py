import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Docker Composeから渡されている環境変数から
# PostgreSQLへの接続URLを取得する
DATABASE_URL = os.environ["DATABASE_URL"]

# SQLAlchemyがDBへ接続するためのEngineを作成する
engine = create_engine(DATABASE_URL)

# DB操作に使用するSessionを生成するための設定
SessionLocal = sessionmaker(bind=engine)


# すべてのSQLAlchemy Modelが継承する基底クラス
class Base(DeclarativeBase):
    pass
