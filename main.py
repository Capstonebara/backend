
from fastapi import FastAPI, Depends, HTTPException, Security
from middleware.http import LogProcessAndTime
from middleware.corn import CORSMiddleware
from routes.collectdata import router
from routes.authentication import authen
from routes import createUser, cms_admin


from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Đảm bảo header Authorization được phép
    expose_headers=["Authorization"],  # Cho phép frontend truy cập header này
)

# Set up HTTP Basic Authentication
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not credentials.username or not credentials.password:
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized", 
            headers={"WWW-Authenticate": "Basic"}
        )
    
    if credentials.username != VALID_USERNAME or credentials.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized", 
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return credentials.username


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API documentation",
        routes=app.routes,
    )

    # Add JWT bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Override Swagger UI route
@app.get("/docs", include_in_schema=False)
def get_docs(username: str = Depends(authenticate)):
    return get_swagger_ui_html(
        openapi_url=app.openapi_url, 
        title="API Documentation",
        swagger_ui_parameters={"persistAuthorization": True}
    )

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
# app.include_router(authen)
# app.include_router(users)
app.include_router(cms_admin.admin)
app.include_router(createUser.residents)