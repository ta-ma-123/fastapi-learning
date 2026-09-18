import asyncio
import threading
import time

from fastapi import APIRouter

router = APIRouter(prefix="/execution-demo", tags=["Execution Demo"])


@router.get("/sync")
def sync_example():
    # 同期的に2秒間待機する
    time.sleep(2)

    return {
        "type": "sync",
        "thread": threading.current_thread().name,
    }


@router.get("/async")
async def async_example():
    # 非同期的に2秒間待機する
    await asyncio.sleep(2)

    return {
        "type": "async",
        "thread": threading.current_thread().name,
    }
