from backend.app.services.chroma_service import search_similar_chunks
from backend.app.models.document import Document
from backend.app.db.database import SessionLocal


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 3,
    user_id: int = None,
):
    candidate_count = 5

    results = search_similar_chunks(
        query=query,
        n_results=candidate_count,
        user_id=user_id,
    )

    db = SessionLocal()

    retrieved_chunks = []

    try:
        for i in range(len(results["ids"][0])):
            document_id = results["metadatas"][0][i]["document_id"]

            document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            retrieved_chunks.append(
                {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "filename": document.filename
                    if document
                    else "Unknown",
                }
            )

        # Chroma already returns candidates ordered by distance.
        # Keep only the best requested number of chunks.
        retrieved_chunks.sort(
            key=lambda chunk: chunk["distance"]
        )

        return retrieved_chunks[:n_results]

    finally:
        db.close()