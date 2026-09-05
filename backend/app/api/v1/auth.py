from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token, decode_access_token
from backend.app.db.database import SessionLocal
from backend.app.schemas.auth import LoginRequest, RegisterRequest
from backend.app.services.auth_service import authenticate_user, register_user

security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(db, data)

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(db, data)

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        return payload

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "user": current_user
    }