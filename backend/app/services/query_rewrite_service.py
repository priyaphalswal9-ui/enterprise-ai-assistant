from backend.app.ai.provider_factory import get_llm_provider


def generate_query_variations(query: str) -> list[str]:
    provider = get_llm_provider()

    prompt = f"""
Generate 3 alternative search queries for the following user query.

The alternative queries should:
- preserve the original meaning
- use different wording
- focus on important entities, facts, and concepts
- be useful for document retrieval

Return exactly 3 queries, one per line.
Do not add numbering or explanations.

User query:
{query}
"""

    response = provider.generate(prompt, [])

    queries = [
        line.strip()
        for line in response.splitlines()
        if line.strip()
    ]

    queries = queries[:3]

    return [query] + queries