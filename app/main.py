from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.routers.books import router as books_router
from app.routers.execution_demo import router as execution_demo_router
from app.routers.products import router as products_router


# STEP3 自力課題
class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str | None = None


# FastAPIアプリケーションを作成する
app = FastAPI()

# CORSでアクセスを許可するオリジン
origins = settings.frontend_origins

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 商品APIのRouterをFastAPIアプリへ登録する
app.include_router(products_router)
# 書籍APIのRouterをFastAPIアプリへ登録する
app.include_router(books_router)
# 同期処理と非同期処理検証用APIのRouterをFastAPIアプリへ登録する
app.include_router(execution_demo_router)


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
