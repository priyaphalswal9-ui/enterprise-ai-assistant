from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.ai.ai_service import AIService
from backend.app.api.v1.auth import get_current_user, get_db
from backend.app.schemas.message import MessageCreate
from backend.app.services.conversation_service import get_conversation
from backend.app.services.message_service import (
    create_message,
    get_conversation_messages,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Messages"],
)


@router.post("/{conversation_id}/messages")
def create_new_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Check whether conversation belongs to current user
    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=int(current_user["sub"]),
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Save user message
    message = create_message(
        db=db,
        conversation_id=conversation_id,
        content=data.content,
        role="user",
    )

    # Get complete conversation history
    conversation_history = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    # Generate AI response using conversation context
    ai_service = AIService()

    assistant_content = ai_service.generate_response(
        data.content,
        conversation_history,
    )

    # Save assistant message
    assistant_message = create_message(
        db=db,
        conversation_id=conversation_id,
        content=assistant_content,
        role="assistant",
    )

    return {
        "user_message": {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        },
        "assistant_message": {
            "id": assistant_message.id,
            "conversation_id": assistant_message.conversation_id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at,
        },
    }


@router.get("/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Check whether conversation belongs to current user
    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=int(current_user["sub"]),
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Fetch conversation history
    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    return [
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]