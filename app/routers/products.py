from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate

router = APIRouter()

products = {
    1: {
        "name": "ノートPC",
        "price": 120000,
        "description": "開発用PC",
    },
    2: {
        "name": "マウス",
        "price": 3000,
        "description": None,
    },
}


@router.get("/products")
def get_products(
    pagination: Annotated[dict, Depends(get_pagination)],
):
    # ページング条件を取得する
    limit = pagination["limit"]
    offset = pagination["offset"]

    # 商品IDを含めた一覧データを作成する
    product_list = [
        {
            "id": product_id,
            **product,
        }
        for product_id, product in products.items()
    ]

    # offsetの位置からlimit件の商品を返す
    return product_list[offset : offset + limit]


@router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
):
    # リクエストデータをもとにSQLAlchemy Modelを作成する
    product = Product(
        name=product_data.name,
        price=product_data.price,
    )

    # 新しい商品をSessionの管理対象に追加する
    db.add(product)

    # DBへ変更を確定する
    db.commit()

    # DBで確定した最新の内容を取得する
    db.refresh(product)

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
    }


@router.get(
    "/products/{product_id}",
    responses={
        404: {
            "description": "Product not found",
        }
    }
)
def get_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # 主キーを指定してproductsテーブルから商品を取得する
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
    }


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    # 更新対象の商品をDBから取得する
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # リクエストされた内容でModelを更新する
    product.name = product_data.name
    product.price = product_data.price

    # DBへ変更を確定する
    db.commit()

    # DBで確定した最新の内容を取得する
    db.refresh(product)

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
    }


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # 削除対象の商品をDBから取得する
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # 商品を削除対象にする
    db.delete(product)

    # DBへ変更を確定する
    db.commit()

    return {
        "message": "Product deleted",
    }


@router.post(
    "/products/{product_id}/duplicate",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {
            "description": "Product not found",
        }
    }
)
def duplicate_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # 主キーを指定してproductsテーブルから商品を取得する
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # 取得した商品をもとにSQLAlchemy Modelを作成する
    new_product = Product(
        name=product.name,
        price=product.price,
    )

    # 新しい商品をSessionの管理対象に追加する
    db.add(new_product)

    # DBへ変更を確定する
    db.commit()

    # DBで確定した最新の内容を取得する
    db.refresh(new_product)

    return {
        "id": new_product.id,
        "name": new_product.name,
        "price": new_product.price,
    }
