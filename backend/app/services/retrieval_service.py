from backend.app.services.chroma_service import search_similar_chunks


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 3,
):
    results = search_similar_chunks(
        query=query,
        n_results=n_results,
    )

    retrieved_chunks = []

    for i in range(len(results["ids"][0])):
        retrieved_chunks.append(
            {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return retrieved_chunks