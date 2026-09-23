import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not configured."
    )