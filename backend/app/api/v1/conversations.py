from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import get_current_user, get_db
from backend.app.schemas.conversation import ConversationCreate
from backend.app.services.conversation_service import (
    create_conversation,
    get_user_conversations,
     get_conversation,
     delete_conversation,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("")
def create_new_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    conversation = create_conversation(
        db=db,
        user_id=int(current_user["sub"]),
        data=data,
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }

@router.get("")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    conversations = get_user_conversations(
        db=db,
        user_id=int(current_user["sub"]),
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]

@router.get("/{conversation_id}")
def get_single_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
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

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }
@router.delete("/{conversation_id}")
def delete_user_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    deleted = delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=int(current_user["sub"]),
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully"
    }