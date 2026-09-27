from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


def test_create_task(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：タスクの登録"""
    # リクエストデータを作成
    title = "a" * 100
    assert len(title) == 100
    explanation = "a" * 1000
    assert len(explanation) == 1000
    request_data = {
        "title": title,
        "explanation": explanation,
        "status": True,
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 201

    # レスポンスボディを検証
    response_data = response.json()
    task_id = response_data["id"]

    assert response_data == {
        "id": task_id,
        "title": title,
        "explanation": explanation,
        "status": True,
    }

    # DBに登録されていることを検証
    task = db_session.get(Task, task_id)
    assert task is not None
    assert task.title == title
    assert task.explanation == explanation
    assert task.status == True


def test_create_task_defaults_explanation_and_status_when_omitted(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：リクエストデータのexplanationとstatusを省略してタスクの登録"""
    # リクエストデータを作成
    request_data = {
        "title": "テストタスク",
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 201

    # レスポンスボディを検証
    response_data = response.json()
    task_id = response_data["id"]

    assert response_data == {
        "id": task_id,
        "title": "テストタスク",
        "explanation": None,
        "status": False,
    }

    # DBに登録されていることを検証
    task = db_session.get(Task, task_id)
    assert task is not None
    assert task.title == "テストタスク"
    assert task.explanation == None
    assert task.status == False


def test_create_task_blank_title(
        client: TestClient,
) -> None:
    """異常系：リクエストデータのtitleをブランクでタスクの登録"""
    # リクエストデータを作成
    request_data = {
        "title": "",
        "explanation": "テストタスクの説明",
        "status": True,
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_create_task_none_title(
        client: TestClient,
) -> None:
    """異常系：リクエストデータのtitleをNoneでタスクの登録"""
    # リクエストデータを作成
    request_data = {
        "title": None,
        "explanation": "テストタスクの説明",
        "status": True,
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_create_task_max_len_over_title(
        client: TestClient,
) -> None:
    """異常系：リクエストデータのtitleが最大文字数オーバーでタスクの登録"""
    # リクエストデータを作成
    data = "a" * 101
    assert len(data) > 100

    request_data = {
        "title": data,
        "explanation": "テストタスクの説明",
        "status": True,
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_create_task_max_len_over_explanation(
        client: TestClient,
) -> None:
    """異常系：リクエストデータのexplanationが最大文字数オーバーでタスクの登録"""
    # リクエストデータを作成
    data = "a" * 1001
    assert len(data) > 1000

    request_data = {
        "title": "テストタスク",
        "explanation": data,
        "status": True,
    }

    # POST APIを実行
    response = client.post(
        "/tasks",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # エラーが発生した項目を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "explanation"]
        for error in errors
    )


def test_get_task_list(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：タスク一覧の取得"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(10):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i <= 5
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # APIを実行してタスク一覧を取得（5件目から3件取得）
    response = client.get(
        "/tasks",
        params={
            "limit": 3,
            "offset": 4,
        }
    )

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを取得
    res_tasks = response.json()

    # 件数の検証
    assert len(res_tasks) == 3

    # レスポンスボディを検証
    assert res_tasks == [
        {
            "id": tasks[4].id,
            "title": "タスク05",
            "explanation": "タスク05の説明",
            "status": True,
        },
        {
            "id": tasks[5].id,
            "title": "タスク06",
            "explanation": "タスク06の説明",
            "status": True,
        },
        {
            "id": tasks[6].id,
            "title": "タスク07",
            "explanation": "タスク07の説明",
            "status": False,
        },
    ]


def test_get_task_list_not_found(
        client: TestClient,
) -> None:
    """正常系：データが存在しない場合"""
    # APIを実行してタスク一覧を取得
    response = client.get(
        "/tasks",
        params={
            "limit": 1,
            "offset": 0,
        }
    )

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを検証
    assert response.json() == []


def test_get_task_list_limit_zero(
        client: TestClient,
) -> None:
    """正常系：limitがゼロの場合"""
    # APIを実行してタスク一覧を取得
    response = client.get(
        "/tasks",
        params={
            "limit": 0,
            "offset": 0,
        }
    )

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを検証
    assert response.json() == []


def test_get_task(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：指定したタスクの取得"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # APIを実行してタスクを取得
    response = client.get(f"/tasks/{tasks[1].id}")

    # HTTPステータスコードを検証する
    assert response.status_code == 200

    # レスポンスの内容を検証する
    assert response.json() == {
        "id": tasks[1].id,
        "title": "タスク02",
        "explanation": "タスク02の説明",
        "status": False,
    }


def test_get_task_not_found(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：指定したタスクが存在しない場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # APIを実行してタスクを取得
    response = client.get("/tasks/999")

    # HTTPステータスコードを検証する
    assert response.status_code == 404

    # レスポンスの内容を検証する
    assert response.json() == {
        "detail": "Task not found",
    }


def test_get_task_invalid_id(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：パスパラメータが不正の場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # APIを実行してタスクを取得
    response = client.get("/tasks/abc")

    # HTTPステータスコードを検証する
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["path", "task_id"]
        for error in errors
    )


def test_update_task(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：タスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": "更新タスク",
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[2].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを検証
    response_data = response.json()

    assert response_data == {
        "id": tasks[2].id,
        "title": "更新タスク",
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # DBに変更が反映されていることを検証
    task = db_session.get(Task, tasks[2].id)
    assert task is not None
    assert task.title == "更新タスク"
    assert task.explanation == "更新タスクの説明"
    assert task.status == True


def test_update_task_defaults_explanation_status_when_omitted(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：リクエストデータのexplanationとstatusを省略してタスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": "更新タスク",
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[0].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを検証
    response_data = response.json()

    assert response_data == {
        "id": tasks[0].id,
        "title": "更新タスク",
        "explanation": None,
        "status": False,
    }

    # DBに変更が反映されていることを検証
    task = db_session.get(Task, tasks[0].id)
    assert task is not None
    assert task.title == "更新タスク"
    assert task.explanation == None
    assert task.status == False


def test_update_task_not_found(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：指定したタスクが存在しない場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": "更新タスク",
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        "/tasks/999",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 404

    # レスポンスの内容を検証する
    assert response.json() == {
        "detail": "Task not found",
    }


def test_update_task_invalid_id(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：パスパラメータが不正の場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": "更新タスク",
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        "/tasks/abc",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["path", "task_id"]
        for error in errors
    )


def test_update_task_blank_title(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：リクエストデータのtitleをブランクでタスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": "",
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[0].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_update_task_none_title(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：リクエストデータのtitleをブランクでタスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    request_data = {
        "title": None,
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[0].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_update_task_max_len_over_title(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：リクエストデータのtitleが最大文字数オーバーでタスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    data = "a" * 101
    assert len(data) > 100

    request_data = {
        "title": data,
        "explanation": "更新タスクの説明",
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[0].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "title"]
        for error in errors
    )


def test_update_task_max_len_over_explanation(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：リクエストデータのexplanationが最大文字数オーバーでタスクの更新"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # リクエストデータを作成
    data = "a" * 1001
    assert len(data) > 1000

    request_data = {
        "title": "更新タスク",
        "explanation": data,
        "status": True,
    }

    # PUT APIを実行
    response = client.put(
        f"/tasks/{tasks[0].id}",
        json=request_data,
    )

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスの内容を検証する
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "explanation"]
        for error in errors
    )


def test_delete_task(
        client: TestClient,
        db_session: Session,
) -> None:
    """正常系：タスクの削除"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # DELETE APIを実行
    response = client.delete(f"/tasks/{tasks[2].id}")

    # HTTPステータスコードを検証
    assert response.status_code == 200

    # レスポンスボディを検証
    assert  response.json() == {
        "message": "Task deleted",
    }

    # DBから削除対象のタスクを検索する
    deleted_task = db_session.execute(
        select(Task).where(Task.id == tasks[2].id)
    ).scalar_one_or_none()

    # タスクがDBに存在しないことを検証する
    assert deleted_task is None


def test_delete_task_not_found(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：指定したタスクが存在しない場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # DELETE APIを実行
    response = client.delete("/tasks/999")

    # HTTPステータスコードを検証
    assert response.status_code == 404

    # レスポンスボディを検証
    assert  response.json() == {
        "detail": "Task not found",
    }


def test_delete_task_invalid_id(
        client: TestClient,
        db_session: Session,
) -> None:
    """異常系：パスパラメータが不正の場合"""
    # テスト用のデータを作成する
    tasks = []
    for i in range(3):
        task_no = str(i + 1).zfill(2)
        task = Task(
            title=f"タスク{task_no}",
            explanation=f"タスク{task_no}の説明",
            status=i % 2 == 0
        )
        tasks.append(task)

    # テストデータを一括登録
    db_session.add_all(tasks)
    db_session.commit()

    # DELETE APIを実行
    response = client.delete("/tasks/abc")

    # HTTPステータスコードを検証
    assert response.status_code == 422

    # レスポンスボディを検証
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["path", "task_id"]
        for error in errors
    )
