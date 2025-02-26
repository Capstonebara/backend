
from fastapi import FastAPI, Depends, HTTPException
from middleware import CORSMiddleware, LogProcessAndTime
from routes.collectdata import router
from routes.authentication import authen
from routes.createUser import users

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
import os

# Load environment variables
load_dotenv()

# Get credentials from the .env file
VALID_USERNAME = os.getenv("VALID_USERNAME")
VALID_PASSWORD = os.getenv("VALID_PASSWORD")

app = FastAPI(docs_url=None, redoc_url=None)

# Set up HTTP Basic Authentication
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not credentials.username or not credentials.password:
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    
    if credentials.username != 'maidung' or credentials.password != '123':
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    
    return credentials.username

# Override Swagger UI route
@app.get("/docs", include_in_schema=False)
def get_docs(username: str = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="Docs")

# Optional: Protect the ReDoc route too
@app.get("/redoc", include_in_schema=False)
def get_redoc(username: str = Depends(authenticate)):
    return get_redoc_html(openapi_url=app.openapi_url, title="ReDoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogProcessAndTime)
app.include_router(router)
app.include_router(authen)
app.include_router(users)