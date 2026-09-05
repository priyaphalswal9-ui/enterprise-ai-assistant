from fastapi import FastAPI

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.conversations import router as conversations_router

app = FastAPI()


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    conversations_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {"message": "Enterprise AI Assistant API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}