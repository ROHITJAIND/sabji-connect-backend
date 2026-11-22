"""WebSocket route for real-time mobile updates."""

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.api.websocket.services import ws_manager
from app.core.auth.jwt import decode_token

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    family_id: str = Query(""),
):
    """Real-time WebSocket endpoint.

    Android clients connect with:
      ws://<host>/api/ws?token=<jwt>&family_id=<family_id>
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub", "unknown")
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    if not family_id:
        family_id = "__global__"

    await ws_manager.connect(websocket, family_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, family_id)
    except Exception:
        await ws_manager.disconnect(websocket, family_id)
