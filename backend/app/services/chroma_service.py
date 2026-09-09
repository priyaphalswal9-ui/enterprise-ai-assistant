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
            }
        ],
    )

def search_similar_chunks(
    query: str,
    n_results: int = 3,
):
    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results

