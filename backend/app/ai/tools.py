DOCUMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_user_documents",
            "description": (
                "List all documents uploaded by the current user. "
                "Use this when the user asks what documents they "
                "have uploaded or wants a list of their documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Search the current user's uploaded documents "
                "for information relevant to a query."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The information to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
]