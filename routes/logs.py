from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

logs = APIRouter()

# websocket

connected_devices: Dict[str, WebSocket] = {}

@logs.websocket("/get-logs/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    connected_devices[device_id] = websocket
    print(f"Device {device_id} connected")

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                print(f"Received from {device_id}: {data}")

    except WebSocketDisconnect:
        print(f"Device {device_id} disconnected")
        del connected_devices[device_id]