from backend.app.ai.provider_factory import get_llm_provider


def should_rewrite_query(query: str) -> bool:
    query = query.strip().lower()

    words = query.split()

    if len(words) <= 6:
        return False

    follow_up_phrases = [
        "why",
        "how",
        "what about",
        "explain",
        "compare",
        "difference",
        "which one",
        "tell me more",
    ]

    return any(
        phrase in query
        for phrase in follow_up_phrases
    )


def generate_query_variations(
    query: str,
) -> list[str]:

    query = query.strip()

    if not query:
        return []

    if not should_rewrite_query(query):
        return [query]

    provider = get_llm_provider()

    prompt = f"""
Generate 2 alternative search queries for the user's query.

Rules:
- Preserve the exact meaning.
- Keep important entities, names, numbers, and technical terms.
- Do not invent information.
- Make each query useful for document retrieval.
- Return exactly 2 queries, one per line.
- Do not add numbering or explanations.

User query:
{query}
"""

    try:
        response = provider.generate(
            prompt=prompt,
            conversation_history=[],
        )

        variations = [
            line.strip()
            for line in response.splitlines()
            if line.strip()
        ]

        variations = variations[:2]

        return [query, *variations]

    except Exception:
        return [query]