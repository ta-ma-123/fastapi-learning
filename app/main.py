from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


# 商品登録時に受け取るデータの構造を定義する
class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    description: str | None = None


# STEP3 自力課題
class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str | None = None


# STEP4 更新用モデル
class ProductUpdate(BaseModel):
    name: str
    price: int = Field(gt=0)
    description: str | None = None


# STEP4 自力課題 書籍登録用
class BookCreate(BaseModel):
    title: str
    price: int = Field(gt=0)
    description: str | None = None


# STEP4 自力課題 書籍更新用
class BookUpdate(BaseModel):
    title: str
    price: int = Field(gt=0)
    description: str | None = None


# FastAPIアプリケーションを作成する
app = FastAPI()


# STEP4 CRUDの動作確認用データ
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


# STEP4 自力課題用データ
books = {}


# GET / にアクセスされたときの処理を定義する
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


# STEP1 自力課題 GET /hello
@app.get("/hello")
def read_hello():
    return {"message": "Hello from my first API!"}


# STEP2 パスパラメータの確認
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
    }


# STEP2 クエリパラメータの確認
@app.get("/users")
def get_users(limit: int | None = None):
    return {
        "limit": limit,
    }


# STEP2 パスパラメータ & クエリパラメータ
@app.get("/users/{user_id}/items")
def get_user_items(
    user_id: int,
    limit: int = 10,
):
    return {
        "user_id": user_id,
        "limit": limit,
    }


# STEP2 自力課題 GET /books/{book_id}/reviews
@app.get("/books/{book_id}/reviews")
def get_book_reviews(
    book_id: int,
    limit: int = 10,
    offset: int | None = None
):
    return {
        "book_id": book_id,
        "limit": limit,
        "offset": offset,
    }


# STEP3 POST /products
@app.post(
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


# STEP3 自力課題 POST /users
@app.post("/users")
def create_user(user: UserCreate):
    # リクエストボディから受け取ったユーザーデータをそのまま返す
    return user


# STEP4 GET
@app.get(
    "/products/{product_id}",
    responses={
        404: {
            "detail": "Product not found",
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


# STEP4 PUT
@app.put("/products/{product_id}")
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


# STEP4 DELETE
@app.delete("/products/{product_id}")
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


# STEP4 自力課題 POST
@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: BookCreate):
    # 現在の書籍IDの最大値から、新しい書籍IDを作成する
    new_book_id = max(books.keys(), default=0) + 1

    # Pydanticモデルを辞書に変換する
    book_data = book.model_dump()

    # 新しい書籍を保存する
    books[new_book_id] = book_data

    # 作成された書籍IDと書籍データを返す
    return {
        "id": new_book_id,
        **book_data,
    }


# STEP4 自力課題 GET
@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = books.get(book_id)

    # 書籍が存在しない場合は404エラーを返す
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book


# STEP4 自力課題 PUT
@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    # 書籍が存在しない場合は404エラーを返す
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    # 指定された書籍IDのデータを更新する
    books[book_id] = book.model_dump()

    return books[book_id]


# STEP4 自力課題 DELETE
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    # 書籍が存在しない場合は404エラーを返す
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    # 指定された書籍IDのデータを削除する
    deleted_book = books.pop(book_id)

    return deleted_book
