from fastapi import FastAPI

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.messages import router as messages_router
from backend.app.api.v1.conversations import router as conversations_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.evaluations import router as evaluations_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    conversations_router,
    prefix="/api/v1",
)

app.include_router(
    messages_router,
    prefix="/api/v1",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
    )

app.include_router(
    evaluations_router,
    prefix="/api/v1"
)

@app.get("/")
def root():
    return {"message": "Enterprise AI Assistant API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}