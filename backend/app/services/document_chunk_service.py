from sqlalchemy.orm import Session

from backend.app.models.document_chunk import DocumentChunk


def create_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
) -> list[DocumentChunk]:

    document_chunks = []

    for index, chunk in enumerate(chunks):
        document_chunk = DocumentChunk(
            document_id=document_id,
            chunk_text=chunk,
            chunk_index=index,
        )

        db.add(document_chunk)
        document_chunks.append(document_chunk)

    db.commit()

    for document_chunk in document_chunks:
        db.refresh(document_chunk)

    return document_chunks