from fastapi import APIRouter, Response

from src.lifecycle import monitor

router = APIRouter()


@router.post("/heartbeat", status_code=204)
def heartbeat() -> Response:
    monitor.record()
    return Response(status_code=204)
