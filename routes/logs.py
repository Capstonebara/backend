from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List
from database import crud, models
from database.database import SessionLocal, engine
from sqlalchemy.orm import Session
import json
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

logs = APIRouter()

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="Bearer"
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

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
        await websocket.accept()
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

# count logs
manager_count = ConnectionManager()

# admin - cms
@logs.websocket("/logs/{device_id}")
async def websocket_logs(websocket: WebSocket, device_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint to receive both text (logs) and binary (images) from a device.
    """
    await device_manager.connect(websocket)
    try:
        while True:
            # Receive a message from the client
            message = await websocket.receive()

            # Check if the message is text or binary
            if "text" in message:
                data = message["text"]

                if data == "ping":
                    print(f"Ping received from device {device_id}")
                    continue

                try:
                    # Parse log data as JSON
                    log_data = json.loads(data)
                    print("Data received:", log_data)

                    # Save log data to the database
                    res = crud.add_logs_to_db(
                        db=db,
                        id=log_data.get("id"),
                        device_id=log_data.get("device_id"),
                        timestamp=int(log_data.get("timestamp")),
                        type=log_data.get("type"),
                    )
                    
                    # Broadcast log data to clients
                    await client_manager.broadcast(json.dumps(res["log"]))
                except json.JSONDecodeError as e:
                    pass

            elif "bytes" in message:
                image_data = message["bytes"]

                # Save the received image to a file
                file_path = f"./data/logs/{res['log']['id']}.jpg"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as img_file:
                    img_file.write(image_data)

                print(f"Image received from device {device_id} and saved to {file_path}")

    except WebSocketDisconnect:
        device_manager.disconnect(websocket)
        print(f"Device {device_id} disconnected")
        

@logs.websocket("/client_logs")
async def stream_client_logs(websocket: WebSocket):
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
def get_recent_logs_for_admin(db: Session = Depends(get_db)):
    return crud.recent_logs(db=db)


@logs.get("/admin/logs_by_day")
def get_daily_logs_for_admin(db: Session = Depends(get_db)):
    return crud.get_logs_by_day(db=db)

@logs.websocket("/admin/logs_total_ws")
async def get_stats_admin(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint để cung cấp dữ liệu logs total theo thời gian thực.
    """
    await manager_count.connect(websocket)
    try:
        while True:
            logs_data = crud.get_stats_admin(db=db)

            logs_json = json.dumps(logs_data)

            await websocket.send_text(logs_json)

            await asyncio.sleep(1)  # Cập nhật mỗi 3 giây
    except WebSocketDisconnect:
        manager_count.disconnect(websocket)
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        manager_count.disconnect(websocket)


@logs.get("/residents/logs_total_residents")
async def stream_log_stats_for_admin(username: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_stats_residents(
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )

@logs.get("/residents/logs_by_day")
def get_user_logs_by_day(username: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.get_logs_by_username(
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    
@logs.get("/residents/recent_logs")
def get_recent_user_logs(username: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.recent_logs_by_username(
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )