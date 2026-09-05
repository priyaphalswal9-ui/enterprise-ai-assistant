from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.schemas.conversation import ConversationCreate


def create_conversation(
    db: Session,
    user_id: int,
    data: ConversationCreate,
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=data.title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
def get_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )

def delete_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> bool:
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )

    if not conversation:
        return False

    db.delete(conversation)
    db.commit()

    return True