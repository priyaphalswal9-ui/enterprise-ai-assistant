import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.messages import router as messages_router
from backend.app.api.v1.conversations import router as conversations_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.evaluations import router as evaluations_router


app = FastAPI(
    title="Nexora API",
    description="AI Knowledge & Workflow Assistant API",
    version="1.0.0",
)


# =========================
# CORS
# =========================

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

allowed_origins = [
    origin.strip()
    for origin in cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API ROUTES
# =========================

API_PREFIX = "/api/v1"


app.include_router(
    auth_router,
    prefix=API_PREFIX,
)

app.include_router(
    conversations_router,
    prefix=API_PREFIX,
)

app.include_router(
    messages_router,
    prefix=API_PREFIX,
)

app.include_router(
    documents_router,
    prefix=API_PREFIX,
)

app.include_router(
    evaluations_router,
    prefix=API_PREFIX,
)


# =========================
# SYSTEM ROUTES
# =========================

@app.get("/")
def root():
    return {
        "message": "Nexora API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }