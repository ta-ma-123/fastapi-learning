from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def test_connect_to_test_database(test_engine: Engine) -> None:
    # テスト用DBに接続する
    with test_engine.connect() as conn:
        # 実際に接続しているデータベース名を取得する
        db_name = conn.execute(
            text("SELECT current_database()")
        ).scalar_one()

    # テスト専用DBへ接続できていることを検証する
    assert db_name == "fastapi_step8_test"


def test_products_table_exists(migrated_engine: Engine) -> None:
    # マイグレーション適用済みDBのテーブル情報を取得する
    inspector = inspect(migrated_engine)

    # テーブルが存在しない場合、実際のテーブル一覧も表示する
    assert inspector.has_table("products"), (
        f"productsテーブルが見つかりません。"
        f"現在のテーブル一覧: {inspector.get_table_names()}"
    )
