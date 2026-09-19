from backend.app.services.chroma_service import (
    search_similar_chunks,
    generate_embedding,
)
from backend.app.services.query_rewrite_service import generate_query_variations
from backend.app.models.document import Document
from backend.app.db.database import SessionLocal


def calculate_cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def mmr_select(query_embedding, chunks, n_results, lambda_param=0.7):
    selected = []
    remaining = chunks.copy()

    while remaining and len(selected) < n_results:
        best_chunk = None
        best_score = float("-inf")

        for chunk in remaining:
            relevance = calculate_cosine_similarity(
                query_embedding,
                chunk["embedding"],
            )

            if selected:
                diversity = max(
                    calculate_cosine_similarity(
                        chunk["embedding"],
                        selected_chunk["embedding"],
                    )
                    for selected_chunk in selected
                )
            else:
                diversity = 0

            mmr_score = (
                lambda_param * relevance
                - (1 - lambda_param) * diversity
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_chunk = chunk

        selected.append(best_chunk)
        remaining.remove(best_chunk)

    return selected


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 5,
    user_id: int = None,
):
    # Retrieve more candidates so relevant chunks are not
    # eliminated before MMR selection.
    candidate_count = 10

    query_variations = generate_query_variations(query)

    all_chunks = {}

    db = SessionLocal()

    try:
        for search_query in query_variations:
            results = search_similar_chunks(
                query=search_query,
                n_results=candidate_count,
                user_id=user_id,
            )

            for i in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][i]

                if chunk_id in all_chunks:
                    continue

                document_id = results["metadatas"][0][i]["document_id"]

                document = (
                    db.query(Document)
                    .filter(Document.id == document_id)
                    .first()
                )

                chunk_text = results["documents"][0][i]

                # Avoid keeping identical chunks from duplicate
                # uploads of the same document.
                duplicate = any(
                    existing["text"] == chunk_text
                    for existing in all_chunks.values()
                )

                if duplicate:
                    continue

                all_chunks[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "filename": (
                        document.filename
                        if document
                        else "Unknown"
                    ),
                    "embedding": generate_embedding(chunk_text),
                }

        candidates = list(all_chunks.values())

        if not candidates:
            return []

        query_embedding = generate_embedding(query)

        selected_chunks = mmr_select(
            query_embedding=query_embedding,
            chunks=candidates,
            n_results=n_results,
        )

        for chunk in selected_chunks:
            chunk.pop("embedding", None)

        return selected_chunks

    finally:
        db.close()