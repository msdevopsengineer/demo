from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Custom Authenticator API",
    description="Secure TOTP Authenticator Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
origins = [
    "http://localhost:3000",  # React Frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.api import api_router
from app.core.config import settings

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Custom Authenticator Service is running"}

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
