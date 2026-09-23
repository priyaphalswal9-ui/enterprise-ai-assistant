from pydantic import BaseModel


class MessageCreate(BaseModel):

    content: str

    document_id: int | None = None


class MessageResponse(BaseModel):

    id: int

    conversation_id: int

    role: str

    content: str

    created_at: str