def build_conversation_context(conversation_history):
    recent_messages = conversation_history[-10:]

    context = []

    for message in recent_messages:
        context.append(
            f"{message.role.upper()}: {message.content}"
        )

    return "\n".join(context)