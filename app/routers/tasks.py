from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.models.task import Task
from app.schemas.tasks import TaskCreate, TaskUpdate

router = APIRouter()


@router.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
):
    # リクエストボディから登録用のモデルを作成
    new_task = Task(
        title=task_data.title,
        explanation=task_data.explanation,
        status=task_data.status,
    )
    # Sessionに登録用モデルを追加
    db.add(new_task)
    # 登録を確定
    db.commit()
    # 登録した内容を取得
    db.refresh(new_task)

    return {
        "id": new_task.id,
        "title": new_task.title,
        "explanation": new_task.explanation,
        "status": new_task.status,
    }


@router.get("/tasks")
def get_tasks(
    pagination: Annotated[dict, Depends(get_pagination)],
    db: Annotated[Session, Depends(get_db)],
):
    # ページング条件を取得
    limit = pagination["limit"]
    offset = pagination["offset"]

    stmt = (
        select(Task)
        .order_by(Task.id)
        .offset(offset)
        .limit(limit)
    )
    result = db.execute(stmt)

    rows = result.scalars().all()

    # 取得結果を辞書に変換
    tasks = []
    for row in rows:
        task = {
            "id": row.id,
            "title": row.title,
            "explanation": row.explanation,
            "status": row.status,
        }

        tasks.append(task)

    return tasks


@router.get(
    "/tasks/{task_id}",
    responses={
        404: {
            "description": "Task not found",
        }
    }
)
def get_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # 主キーを指定してテーブルからタスクを取得
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {
        "id": task.id,
        "title": task.title,
        "explanation": task.explanation,
        "status": task.status,
    }


@router.put(
    "/tasks/{task_id}",
    responses={
        404: {
            "description": "Task not found",
        }
    }
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    # 更新対象のタスクをテーブルから取得
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # 更新データの作成
    task.title = task_data.title
    task.explanation = task_data.explanation
    task.status = task_data.status

    # コミット
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "explanation": task.explanation,
        "status": task.status,
    }


@router.delete(
    "/tasks/{task_id}",
    responses={
        404: {
            "description": "Task not found",
        }
    }
)
def delete_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # 削除対象のタスクをテーブルから取得
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # タスクを削除対象とする
    db.delete(task)
    # コミット
    db.commit()

    return {
        "message": "Task deleted",
    }
