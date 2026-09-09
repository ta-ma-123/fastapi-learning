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
