from fastapi import FastAPI

# FastAPIアプリケーションを作成する
app = FastAPI()


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
