from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.product import Product


def test_product_create_rollback(
    client: TestClient,
    db_session: Session,
    migrated_engine: Engine,
) -> None:
    # ロールバック確認用の商品名
    name = "pytest_rollback_check"

    # 前回のテストデータが残っていないことを確認する
    with migrated_engine.connect() as connection:
        result = connection.execute(
            select(Product.id).where(Product.name == name)
        ).first()

        assert result is None

    # API経由で商品を登録する
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": 1000,
        },
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    # テスト用Sessionから登録データを取得できることを確認する
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.name == name

    # 別のConnectionからは未確定データが見えないことを確認する
    with migrated_engine.connect() as connection:
        result = connection.execute(
            select(Product.id).where(Product.id == product_id)
        ).first()

        assert result is None


def test_get_product(
    client: TestClient,
    db_session: Session,
) -> None:
    # テスト用の商品データを作成する
    product = Product(
        name="テスト商品",
        price=1500,
    )

    # テスト用DBへ商品を登録する
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # 登録した商品のIDを指定してGET APIを呼び出す
    response = client.get(f"/products/{product.id}")

    # HTTPステータスコードを検証する
    assert response.status_code == 200

    # レスポンスの内容を検証する
    assert response.json() == {
        "id": product.id,
        "name": "テスト商品",
        "price": 1500,
    }


def test_create_product(
    client: TestClient,
    db_session: Session,
) -> None:
    # 商品登録APIへ送信するリクエストデータ
    request_data = {
        "name": "POST正常系テスト商品",
        "price": 2500,
    }

    # 商品登録APIを呼び出す
    response = client.post(
        "/products",
        json=request_data,
    )

    # ステータスコードが201であることを検証する
    assert response.status_code == 201

    # レスポンスの内容を検証する
    response_data = response.json()
    product_id = response_data["id"]

    assert response_data == {
        "id": product_id,
        "name": "POST正常系テスト商品",
        "price": 2500,
    }

    # DBに商品が登録されていることを検証する
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.name == "POST正常系テスト商品"
    assert product.price == 2500


def test_update_product(
    client: TestClient,
    db_session: Session,
) -> None:
    # 更新対象の商品を準備する
    product = Product(
        name="更新前の商品",
        price=1000,
    )

    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    product_id = product.id

    # 商品更新APIを呼び出す
    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "更新後の商品",
            "price": 2000,
        },
    )

    # ステータスコードとレスポンスを検証する
    assert response.status_code == 200

    assert response.json() == {
        "id": product_id,
        "name": "更新後の商品",
        "price": 2000,
    }

    # DBから最新の状態を再取得する
    db_session.refresh(product)

    # DBのデータが更新されていることを検証する
    assert product.name == "更新後の商品"
    assert product.price == 2000


def test_delete_product(
    client: TestClient,
    db_session: Session,
) -> None:
    # 削除対象の商品を準備する
    product = Product(
        name="削除テスト商品",
        price=1000,
    )

    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    product_id = product.id

    # 商品削除APIを呼び出す
    response = client.delete(f"/products/{product_id}")

    # ステータスコードとレスポンスを検証する
    assert response.status_code == 200

    assert response.json() == {
        "message": "Product deleted",
    }

    # DBから削除対象の商品を検索する
    deleted_product = db_session.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    # 商品がDBに存在しないことを検証する
    assert deleted_product is None


def test_get_product_not_found(
    client: TestClient,
) -> None:
    # 存在しない商品IDを指定してGET APIを呼び出す
    response = client.get("/products/-1")

    # HTTPステータスコードを検証する
    assert response.status_code == 404

    # エラーレスポンスの内容を検証する
    assert response.json() == {
        "detail": "Product not found",
    }


def test_get_product_invalid_id(
    client: TestClient,
) -> None:
    # 商品IDに整数へ変換できない文字列を指定する
    response = client.get("/products/abc")

    # バリデーションエラーが返ることを検証する
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["path", "product_id"]
        for error in errors
    )


def test_update_product_not_found(
    client: TestClient,
) -> None:
    # 存在しない商品IDを指定して更新APIを呼び出す
    response = client.put(
        "/products/-1",
        json={
            "name": "更新テスト商品",
            "price": 2000,
        },
    )

    # 商品が存在しない場合は404が返ることを検証する
    assert response.status_code == 404

    # エラーレスポンスの内容を検証する
    assert response.json() == {
        "detail": "Product not found",
    }


def test_delete_product_not_found(
    client: TestClient,
) -> None:
    # 存在しない商品IDを指定して削除APIを呼び出す
    response = client.delete("/products/-1")

    # 商品が存在しない場合は404が返ることを検証する
    assert response.status_code == 404

    # エラーレスポンスの内容を検証する
    assert response.json() == {
        "detail": "Product not found",
    }


def test_create_product_invalid_price(
    client: TestClient,
) -> None:
    # 価格に整数へ変換できない文字列を指定する
    response = client.post(
        "/products",
        json={
            "name": "テスト商品",
            "price": "abc",
        },
    )

    # バリデーションエラーが返ることを検証する
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "price"]
        for error in errors
    )


def test_create_product_missing_name(
    client: TestClient,
) -> None:
    # 必須項目のnameを省略して商品登録APIを呼び出す
    response = client.post(
        "/products",
        json={
            "price": 1000,
        },
    )

    # バリデーションエラーが返ることを検証する
    assert response.status_code == 422

    # nameがエラーの対象になっていることを検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "name"]
        for error in errors
    )


def test_duplicate_product(
    client: TestClient,
    db_session: Session,
) -> None:
    # 複製元の商品を準備する
    product = Product(
        name="テスト商品",
        price=1000,
    )

    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # 複製APIを呼び出す
    response = client.post(
        f"/products/{product.id}/duplicate",
    )

    # 正常のステータスコードが返ることを確認
    assert response.status_code == 201

    # レスポンスを取得
    response_data = response.json()

    # 複製後の商品を確認
    assert response_data == {
        "id": response_data["id"],
        "name": "テスト商品",
        "price": 1000,
    }

    # 複製元の商品を取得
    base_product = db_session.execute(
        select(Product).where(Product.id == product.id)
    ).scalar_one_or_none()

    # 複製元の商品がDBに存在することを確認
    assert base_product is not None

    # 複製後の商品を取得
    copied_product = db_session.execute(
        select(Product).where(Product.id == response_data["id"])
    ).scalar_one_or_none()

    # 複製後の商品がDBに存在することを確認
    assert copied_product is not None

    # 複製元と複製後の商品の比較
    # 商品IDが異なる
    assert base_product.id != copied_product.id
    # 商品名と価格は同じ
    assert base_product.name == copied_product.name
    assert base_product.price == copied_product.price
