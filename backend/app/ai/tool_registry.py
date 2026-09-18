from backend.app.services.document_tool_service import (
    list_user_documents,
    search_documents,
)


TOOL_HANDLERS = {
    "list_user_documents": list_user_documents,
    "search_documents": search_documents,
}


def get_tool_handler(tool_name: str):
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    return handler