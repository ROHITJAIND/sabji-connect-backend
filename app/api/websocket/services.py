"""WebSocket connection manager for real-time order and catalog updates."""

import asyncio
import json
from typing import Any

from fastapi import WebSocket

from app.core.logger import logger


class ConnectionManager:
    """Manages WebSocket connections grouped by family_id.

    Broadcasts order changes to family members in real time.
    """

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, family_id: str, user_id: str) -> None:
        await websocket.accept()
        async with self._lock:
            if family_id not in self._connections:
                self._connections[family_id] = set()
            self._connections[family_id].add(websocket)
        logger.info("WS connected: user=%s family=%s (total=%d)", user_id, family_id, len(self._connections.get(family_id, set())))

    async def disconnect(self, websocket: WebSocket, family_id: str) -> None:
        async with self._lock:
            conns = self._connections.get(family_id)
            if conns:
                conns.discard(websocket)
                if not conns:
                    del self._connections[family_id]
        logger.info("WS disconnected: family=%s", family_id)

    async def broadcast_to_family(self, family_id: str, event: str, data: Any = None) -> None:
        """Send a JSON message to all connected members of a family."""
        message = json.dumps({"event": event, "data": data})
        async with self._lock:
            conns = self._connections.get(family_id, set()).copy()

        stale: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)

        if stale:
            async with self._lock:
                for ws in stale:
                    self._connections.get(family_id, set()).discard(ws)

    async def broadcast_to_all(self, event: str, data: Any = None) -> None:
        """Broadcast to every connected client."""
        message = json.dumps({"event": event, "data": data})
        async with self._lock:
            all_conns = [ws for conns in self._connections.values() for ws in conns]

        for ws in all_conns:
            try:
                await ws.send_text(message)
            except Exception:
                pass


ws_manager = ConnectionManager()
