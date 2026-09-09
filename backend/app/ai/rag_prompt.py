def build_rag_prompt(
    query: str,
    rag_context: str,
) -> str:
    return f"""
Answer the user's question using the provided context.

If the answer cannot be found in the context, clearly say that the information is not available in the provided documents.

Context:
{rag_context}

User Question:
{query}

Answer:
""".strip()