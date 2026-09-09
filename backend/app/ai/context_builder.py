def build_conversation_context(conversation_history):
    recent_messages = conversation_history[-10:]

    context = []

    for message in recent_messages:
        context.append(
            f"{message.role.upper()}: {message.content}"
        )

    return "\n".join(context)

def build_rag_context(retrieved_chunks: list[dict]) -> str:
    context = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context.append(
            f"[Context {index}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context)