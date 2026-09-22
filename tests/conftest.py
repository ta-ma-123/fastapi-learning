from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_db
from app.main import app

# Docker Composeで定義したテスト用DBの接続先
TEST_DB_HOST = "test-db"
TEST_DB_NAME = "fastapi_step8_test"


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    # 既存のDB接続設定を取得する
    development_url = make_url(settings.database_url)

    # 開発用DBの設定がテスト用DBを指していないことを確認する
    if (
        development_url.host == TEST_DB_HOST
        or development_url.database == TEST_DB_NAME
    ):
        raise RuntimeError("開発用DBの接続設定を確認してください")

    # ホスト名とDB名をテスト用に変更する
    test_url = development_url.set(
        host=TEST_DB_HOST,
        port=5432,
        database=TEST_DB_NAME,
    )

    # テスト専用のEngineを作成する
    engine = create_engine(test_url)

    try:
        # テスト側へEngineを渡す
        yield engine
    finally:
        # テスト終了後に接続プールを破棄する
        engine.dispose()


@pytest.fixture(scope="session")
def migrated_engine(test_engine: Engine) -> Engine:
    # テスト用DBへ接続し、トランザクションを開始する
    with test_engine.begin() as connection:

        # 実際の接続先DB名を取得する
        db_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

        # 開発用DBへの誤適用を防止する
        if (
            test_engine.url.host != TEST_DB_HOST
            or db_name != TEST_DB_NAME
        ):
            raise RuntimeError("テスト用DB以外にはマイグレーションできません")

        # プロジェクトルートのalembic.iniを読み込む
        alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
        alembic_config = Config(str(alembic_ini))

        # Alembicへテスト用DBのConnectionを渡す
        alembic_config.attributes["connection"] = connection

        # テスト用DBを最新のマイグレーションまで更新する
        command.upgrade(alembic_config, "head")

    # マイグレーション適用済みのEngineを返す
    return test_engine


@pytest.fixture
def db_session(migrated_engine: Engine) -> Iterator[Session]:
    # テスト用DBへ接続する
    with migrated_engine.connect() as connection:

        # テスト全体を囲むトランザクションを開始する
        transaction = connection.begin()

        try:
            # API内のcommit()が外側のトランザクションを
            # 確定しないようにSAVEPOINTを使用する
            with Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session

        finally:
            # テストで変更したデータを元に戻す
            transaction.rollback()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:

    # 通常のget_db()の代わりにテスト用Sessionを返す
    def override_get_db() -> Iterator[Session]:
        yield db_session

    # FastAPIのDB依存性をテスト用に差し替える
    app.dependency_overrides[get_db] = override_get_db

    try:
        # テスト用のAPIクライアントを作成する
        with TestClient(app) as test_client:
            yield test_client

    finally:
        # テスト終了後、今回設定した依存性の差し替えを解除する
        app.dependency_overrides.pop(get_db, None)
