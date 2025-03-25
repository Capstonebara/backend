from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from database import crud, models
from database.database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import Depends
import json
import asyncio


logs = APIRouter()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self):
        # Danh sách các WebSocket đang hoạt động
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Chấp nhận kết nối WebSocket và thêm vào danh sách kết nối đang hoạt động.
        """
        await websocket.accept()  # Chấp nhận kết nối
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Xóa kết nối khỏi danh sách khi client ngắt kết nối.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Gửi dữ liệu đến tất cả các kết nối đang hoạt động.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Failed to send message: {e}")


device_manager = ConnectionManager()
client_manager = ConnectionManager()


@logs.websocket("/logs/{device_id}")
async def websocket_logs(websocket: WebSocket, device_id: str, db: Session = Depends(get_db)):
    """
    Endpoint nhận log từ thiết bị và lưu vào database.
    """
    await device_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                continue

            # Parse dữ liệu JSON
            log_data = json.loads(data)

            # Lưu log vào database
            crud.add_logs_to_db(
                db=db,
                id=log_data.get("id"),
                device_id=log_data.get("device_id"),
                name=log_data.get("name"),
                photoUrl=log_data.get("photoUrl"),
                timestamp=int(log_data.get("timestamp")),
                type=log_data.get("type"),
                apartment=log_data.get("apartment"),
            )

            print(f"Log received and saved: {log_data}")

            # send log -> client
            await client_manager.broadcast(json.dumps(log_data))

    except WebSocketDisconnect:
        device_manager.disconnect(websocket)
        print(f"Device {device_id} disconnected")

@logs.websocket("/client_logs")
async def websocket_client_logs(websocket: WebSocket):
    """
    Endpoint gửi log đến Next.js hoặc các client khác.
    """
    await client_manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        client_manager.disconnect(websocket)
        print("Client disconnected")

@logs.get("/admin/recent_logs")
def get_recent_logs(db: Session = Depends(get_db)):
    return crud.recent_logs(db=db)


@logs.get("/admin/logs_by_day")
def get_logs_by_day(db: Session = Depends(get_db)):
    return crud.get_logs_by_day(db=db)
