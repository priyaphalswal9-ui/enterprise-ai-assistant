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


# ---------------------------------------------------------
# Normal Message Endpoint
# ---------------------------------------------------------

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
    try:
        message = create_message(
            db=db,
            conversation_id=conversation_id,
            content=data.content,
            role="user",
        )
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save user message",
        )

    # Get conversation history
    conversation_history = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    # Generate AI response
    ai_service = AIService()

    try:
        ai_result = ai_service.generate_response(
            data.content,
            conversation_history,
            user_id=int(current_user["sub"]),
        )

        assistant_content = ai_result["answer"]
        sources = ai_result["sources"]

    except RuntimeError:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again.",
        )

    # Save assistant response
    try:
        assistant_message = create_message(
            db=db,
            conversation_id=conversation_id,
            content=assistant_content,
            role="assistant",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save assistant message",
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
        "sources": sources,
    }


# ---------------------------------------------------------
# Streaming Message Endpoint
# ---------------------------------------------------------
#
# Currently this endpoint intentionally uses the same
# reliable complete-response flow as the normal endpoint.
#
# Proper token streaming will be revisited during frontend
# integration.
#
# ---------------------------------------------------------

@router.post("/{conversation_id}/messages/stream")
def create_streaming_message(
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
    try:
        message = create_message(
            db=db,
            conversation_id=conversation_id,
            content=data.content,
            role="user",
        )
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save user message",
        )

    # Get conversation history
    conversation_history = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    # Generate complete AI response
    ai_service = AIService()

    try:
        ai_result = ai_service.generate_response(
            data.content,
            conversation_history,
            user_id=int(current_user["sub"]),
        )

        assistant_content = ai_result["answer"]
        sources = ai_result["sources"]

    except RuntimeError:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again.",
        )

    # Save assistant response
    try:
        assistant_message = create_message(
            db=db,
            conversation_id=conversation_id,
            content=assistant_content,
            role="assistant",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save assistant message",
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
        "sources": sources,
    }


# ---------------------------------------------------------
# Get Conversation Messages
# ---------------------------------------------------------

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