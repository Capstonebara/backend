import uvicorn
from logging_config import LOGGING_CONFIG

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True, timeout_keep_alive=120, log_config=LOGGING_CONFIG)