def get_pagination(limit: int = 10, offset: int = 0):
    # 一覧取得で使用するページング条件をまとめて返す
    return {
        "limit": limit,
        "offset": offset,
    }
