import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.app.core.config import (
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    QDRANT_URL,
)
from backend.app.services.embedding_service import generate_embedding


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def _point_id(chunk_id: str) -> str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            chunk_id,
        )
    )


def _ensure_payload_indexes():
    """
    Create payload indexes required for filtered retrieval.
    Safe to call repeatedly because Qdrant keeps the existing index.
    """

    client.create_payload_index(
        collection_name=QDRANT_COLLECTION_NAME,
        field_name="user_id",
        field_schema=models.PayloadSchemaType.INTEGER,
    )

    client.create_payload_index(
        collection_name=QDRANT_COLLECTION_NAME,
        field_name="document_id",
        field_schema=models.PayloadSchemaType.INTEGER,
    )


def _ensure_collection(vector_size: int):
    if not client.collection_exists(
        QDRANT_COLLECTION_NAME
    ):
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    _ensure_payload_indexes()


def add_document_chunk(
    chunk_id: str,
    text: str,
    document_id: int,
    chunk_index: int,
    user_id: int,
):
    embedding = generate_embedding(text)

    _ensure_collection(
        vector_size=len(embedding)
    )

    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=_point_id(chunk_id),
                vector=embedding,
                payload={
                    "text": text,
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "user_id": user_id,
                },
            )
        ],
    )


def search_similar_chunks(
    query: str,
    n_results: int = 5,
    user_id: int = None,
    document_id: int = None,
):
    query_embedding = generate_embedding(query)

    _ensure_collection(
        vector_size=len(query_embedding)
    )

    conditions = []

    if user_id is not None:
        conditions.append(
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(
                    value=user_id,
                ),
            )
        )

    if document_id is not None:
        conditions.append(
            models.FieldCondition(
                key="document_id",
                match=models.MatchValue(
                    value=document_id,
                ),
            )
        )

    query_filter = None

    if conditions:
        query_filter = models.Filter(
            must=conditions,
        )

    results = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=n_results,
        with_payload=True,
        with_vectors=True,
    ).points

    return {
        "ids": [[
            str(point.id)
            for point in results
        ]],
        "documents": [[
            point.payload.get("text", "")
            for point in results
        ]],
        "metadatas": [[
            {
                "document_id": point.payload.get(
                    "document_id"
                ),
                "chunk_index": point.payload.get(
                    "chunk_index"
                ),
                "user_id": point.payload.get(
                    "user_id"
                ),
            }
            for point in results
        ]],
        "distances": [[
            1 - point.score
            for point in results
        ]],
        "embeddings": [[
            point.vector
            for point in results
        ]],
    }


def delete_document_chunks(
    document_id: int,
):
    if not client.collection_exists(
        QDRANT_COLLECTION_NAME
    ):
        return

    client.delete(
        collection_name=QDRANT_COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(
                            value=document_id,
                        ),
                    )
                ]
            )
        ),
    )