import chromadb

from backend.app.services.embedding_service import generate_embedding


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


def add_document_chunk(
    chunk_id: str,
    text: str,
    document_id: int,
    chunk_index: int,
    user_id: int,
):
    embedding = generate_embedding(text)

    collection.add(
        ids=[chunk_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[
            {
                "document_id": document_id,
                "chunk_index": chunk_index,
                "user_id": user_id,
            }
        ],
    )

def search_similar_chunks(
    query: str,
    n_results: int = 3,
    user_id: int = None,
):
    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"user_id": user_id},

    )

    return results

