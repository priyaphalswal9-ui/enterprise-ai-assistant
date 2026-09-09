from backend.app.services.chroma_service import search_similar_chunks
from backend.app.models.document import Document
from backend.app.db.database import SessionLocal


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 3,
):
    results = search_similar_chunks(
        query=query,
        n_results=n_results,
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
                    "filename": document.filename if document else "Unknown",
                }
            )

        return retrieved_chunks

    finally:
        db.close()