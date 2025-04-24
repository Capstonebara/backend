# logging_config.py
import logging
from uvicorn.config import LOGGING_CONFIG

# Copy default config và chỉnh sửa format
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s | %(levelname)s | %(message)s"

# Tuỳ chọn định dạng thời gian
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"