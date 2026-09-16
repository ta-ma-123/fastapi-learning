from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    # 1リクエストで使用するSessionを作成する
    db = SessionLocal()

    try:
        # APIへSessionを渡す
        yield db
    finally:
        # APIの処理終了後にSessionを閉じる
        db.close()


def get_pagination(limit: int = 10, offset: int = 0):
    # 一覧取得で使用するページング条件をまとめて返す
    return {
        "limit": limit,
        "offset": offset,
    }
