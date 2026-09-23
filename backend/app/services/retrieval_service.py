from backend.app.services.chroma_service import (
    search_similar_chunks,
    generate_embedding,
)
from backend.app.services.query_rewrite_service import (
    generate_query_variations,
)
from backend.app.models.document import Document
from backend.app.db.database import SessionLocal


def calculate_cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def rerank_candidates(
    query_embedding,
    chunks,
):
    """
    Rank candidates according to their semantic
    similarity with the original user query.
    """

    for chunk in chunks:
        chunk["relevance_score"] = calculate_cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

    return sorted(
        chunks,
        key=lambda chunk: chunk["relevance_score"],
        reverse=True,
    )


def filter_by_relevance(
    chunks,
    min_relative_score=0.65,
):
    """
    Remove candidates that are substantially weaker
    than the best retrieved candidate.

    Relative scoring is used instead of a fixed cosine
    threshold because similarity ranges can vary between
    different queries.
    """

    if not chunks:
        return []

    best_score = chunks[0]["relevance_score"]

    if best_score <= 0:
        return []

    filtered_chunks = []

    for chunk in chunks:
        relative_score = (
            chunk["relevance_score"] / best_score
        )

        if relative_score >= min_relative_score:
            filtered_chunks.append(chunk)

    return filtered_chunks


def mmr_select(
    query_embedding,
    chunks,
    n_results,
    lambda_param=0.7,
):
    """
    Select relevant and diverse chunks using
    Maximal Marginal Relevance.
    """

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
                diversity = 0.0

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
    query,
    n_results=5,
    user_id=None,
    document_id=None,
):
    """
    Advanced retrieval pipeline:

    1. Generate query variations
    2. Retrieve candidate chunks
    3. Deduplicate candidates
    4. Rerank by semantic relevance
    5. Remove weak candidates
    6. Apply MMR for relevance + diversity
    7. Return final chunks
    """

    candidate_count = 10

    query_variations = generate_query_variations(query)

    all_chunks = {}

    db = SessionLocal()

    try:
        # --------------------------------------------------
        # 1. Candidate retrieval
        # --------------------------------------------------
        for search_query in query_variations:
            results = search_similar_chunks(
                query=search_query,
                n_results=candidate_count,
                user_id=user_id,
                document_id=document_id,
            )

            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            embeddings = results.get("embeddings")

            # Chroma may return embeddings as a NumPy array.
            # Never use `if embeddings` here.
            if embeddings is not None:
                embeddings = embeddings[0]

            for i in range(len(ids)):
                chunk_id = ids[i]

                if chunk_id in all_chunks:
                    continue

                metadata = metadatas[i]

                document_id_from_chunk = metadata["document_id"]

                document = (
                    db.query(Document)
                    .filter(
                        Document.id == document_id_from_chunk
                    )
                    .first()
                )

                chunk_text = documents[i]

                # --------------------------------------------------
                # 2. Text-level deduplication
                # --------------------------------------------------
                duplicate = any(
                    existing["text"] == chunk_text
                    for existing in all_chunks.values()
                )

                if duplicate:
                    continue

                # --------------------------------------------------
                # 3. Use stored embedding when available
                # --------------------------------------------------
                if embeddings is not None:
                    chunk_embedding = embeddings[i]
                else:
                    chunk_embedding = generate_embedding(
                        chunk_text
                    )

                all_chunks[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": metadata,
                    "distance": distances[i],
                    "filename": (
                        document.filename
                        if document
                        else "Unknown"
                    ),
                    "embedding": chunk_embedding,
                }

        candidates = list(all_chunks.values())

        if not candidates:
            return []

        # --------------------------------------------------
        # 4. Original query embedding
        # --------------------------------------------------
        query_embedding = generate_embedding(query)

        # --------------------------------------------------
        # 5. Semantic reranking
        # --------------------------------------------------
        candidates = rerank_candidates(
            query_embedding=query_embedding,
            chunks=candidates,
        )

        if not candidates:
            return []

        # --------------------------------------------------
        # 6. Relative relevance filtering
        # --------------------------------------------------
        candidates = filter_by_relevance(
            chunks=candidates,
            min_relative_score=0.65,
        )

        if not candidates:
            return []

        # --------------------------------------------------
        # 7. MMR selection
        # --------------------------------------------------
        selected_chunks = mmr_select(
            query_embedding=query_embedding,
            chunks=candidates,
            n_results=n_results,
        )

        # --------------------------------------------------
        # 8. Remove internal fields
        # --------------------------------------------------
        for chunk in selected_chunks:
            chunk.pop("embedding", None)
            chunk.pop("relevance_score", None)

        return selected_chunks

    finally:
        db.close()