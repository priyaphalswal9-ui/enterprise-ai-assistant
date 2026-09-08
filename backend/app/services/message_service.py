from sqlalchemy.orm import Session

from backend.app.models.message import Message
from backend.app.schemas.message import MessageCreate


def create_message(
    db: Session,
    conversation_id: int,
    data: MessageCreate,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def get_conversation_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )