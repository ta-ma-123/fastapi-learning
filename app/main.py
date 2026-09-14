from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.routers.books import router as books_router
from app.routers.products import router as products_router


# STEP3 自力課題
class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str | None = None


# FastAPIアプリケーションを作成する
app = FastAPI()

# 商品APIのRouterをFastAPIアプリへ登録する
app.include_router(products_router)
# 書籍APIのRouterをFastAPIアプリへ登録する
app.include_router(books_router)


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


# STEP3 自力課題 POST /users
@app.post("/users")
def create_user(user: UserCreate):
    # リクエストボディから受け取ったユーザーデータをそのまま返す
    return user
