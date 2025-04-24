import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True, timeout_keep_alive=120)

# To run the server, use the command:
# gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5500 --workers 4 --timeout 120 --log-config logging.ini