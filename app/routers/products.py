from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_pagination
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
def create_product(product: ProductCreate):
    # 現在の商品IDの最大値から、新しい商品IDを作成する
    new_product_id = max(products.keys(), default=0) + 1

    # Pydanticモデルを辞書に変換する
    product_data = product.model_dump()

    # 新しい商品を保存する
    products[new_product_id] = product_data

    # 作成された商品IDと商品データを返す
    return {
        "id": new_product_id,
        **product_data,
    }


@router.get(
    "/products/{product_id}",
    responses={
        404: {
            "description": "Product not found",
        }
    }
)
def get_product(product_id: int):
    # 指定された商品IDの商品を取得する
    product = products.get(product_id)

    # 商品が存在しない場合は404エラーを返す
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    # 商品が存在しない場合は404エラーを返す
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # 指定された商品IDのデータを更新する
    products[product_id] = product.model_dump()

    return products[product_id]


@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    # 商品が存在しない場合は404エラーを返す
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # 指定された商品IDのデータを削除する
    deleted_product = products.pop(product_id)

    return deleted_product
