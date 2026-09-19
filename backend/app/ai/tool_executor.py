from sqlalchemy.orm import Session

from backend.app.ai.tool_registry import (
    get_tool_handler,
)


def execute_tool(
    tool_name: str,
    arguments: dict,
    db: Session,
    user_id: int,
):
    handler = get_tool_handler(tool_name)

    if tool_name == "list_user_documents":
        return handler(
            db=db,
            user_id=user_id,
        )

    return handler(
        db=db,
        user_id=user_id,
        **arguments,
    )