"""
Simple WebSocket manager for broadcasting realtime events to connected clients.
Lightweight in-memory implementation. For production, replace with Redis/pubsub.
"""
from typing import List
from fastapi import WebSocket
import asyncio
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a JSON-serializable message to all connected clients."""
        text = json.dumps(message)
        async with self.lock:
            to_remove = []
            for ws in list(self.active_connections):
                try:
                    await ws.send_text(text)
                except Exception:
                    to_remove.append(ws)
            for ws in to_remove:
                if ws in self.active_connections:
                    self.active_connections.remove(ws)

# Global manager instance
manager = WebSocketManager()
