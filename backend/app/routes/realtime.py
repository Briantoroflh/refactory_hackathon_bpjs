"""
WebSocket endpoint for realtime updates.
Clients should connect to /ws and the server will verify access_token cookie.
"""
from fastapi import APIRouter, WebSocket, Cookie
from app.services.realtime import manager

# verify_token helper is available in app.services
from app.services import verify_token

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, access_token: str | None = Cookie(None)):
    # Verify access token provided as httpOnly cookie
    if not access_token:
        await websocket.close(code=1008)
        return
    payload = None
    try:
        payload = verify_token(access_token)
    except Exception:
        payload = None
    if not payload:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        # Keep connection open; handle incoming pings/msgs if needed
        while True:
            await websocket.receive_text()
            # No-op: server pushes events via manager.broadcast
    except Exception:
        pass
    finally:
        await manager.disconnect(websocket)
