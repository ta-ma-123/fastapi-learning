from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_pagination
from app.schemas.books import BookCreate, BookUpdate

router = APIRouter()

books = {}


@router.get("/books")
def get_books(
    pagination: Annotated[dict, Depends(get_pagination)],
):
    # ページング条件を取得する
    limit = pagination["limit"]
    offset = pagination["offset"]

    # 書籍IDを含めた一覧データを作成する
    book_list = [
        {
            "id": book_id,
            **book,
        }
        for book_id, book in books.items()
    ]

    # offsetの位置からlimit件の書籍を返す
    return book_list[offset : offset + limit]


@router.post(
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


@router.get("/books/{book_id}")
def get_book(book_id: int):
    book = books.get(book_id)

    # 書籍が存在しない場合は404エラーを返す
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book


@router.put("/books/{book_id}")
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


@router.delete("/books/{book_id}")
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


@router.get("/books/{book_id}/reviews")
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
