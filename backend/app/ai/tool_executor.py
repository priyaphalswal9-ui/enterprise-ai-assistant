from sqlalchemy.orm import Session

from backend.app.services.document_tool_service import (
    list_user_documents,
)


def execute_tool(
    tool_name: str,
    arguments: dict,
    db: Session,
    user_id: int,
):
    if tool_name == "list_user_documents":
        return list_user_documents(
            db=db,
            user_id=user_id,
        )

    raise ValueError(
        f"Unknown tool: {tool_name}"
    )