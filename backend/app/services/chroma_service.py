import chromadb

from backend.app.services.embedding_service import (
    generate_embedding,
)


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
    n_results: int = 5,
    user_id: int = None,
    document_id: int = None,
):
    query_embedding = generate_embedding(query)

    filters = []

    if user_id is not None:
        filters.append(
            {"user_id": user_id}
        )

    if document_id is not None:
        filters.append(
            {"document_id": document_id}
        )

    if len(filters) == 1:
        where = filters[0]

    elif len(filters) > 1:
        where = {
            "$and": filters
        }

    else:
        where = None

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": [
            "documents",
            "metadatas",
            "distances",
            "embeddings",
        ],
    }

    if where is not None:
        query_kwargs["where"] = where

    return collection.query(
        **query_kwargs
    )
def delete_document_chunks(
    document_id: int,
):
    results = collection.get(
        where={
            "document_id": document_id
        }
    )

    ids = results.get(
        "ids",
        []
    )

    if ids:
        collection.delete(
            ids=ids
        )