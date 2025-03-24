from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

logs = APIRouter()

# Class để quản lý kết nối
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        print(f"Device {device_id} connected")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            print(f"Device {device_id} disconnected")

    async def send_message(self, device_id: str, message: str):
        if device_id in self.active_connections:
            await self.active_connections[device_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()

@logs.websocket("/logs/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await manager.connect(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_message(device_id, "pong")
            else:
                print(f"Received from {device_id}: {data}")
                # Xử lý log ở đây (ví dụ lưu vào database)
    except WebSocketDisconnect:
        manager.disconnect(device_id)