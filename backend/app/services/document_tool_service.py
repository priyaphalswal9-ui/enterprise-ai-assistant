from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.services.retrieval_service import retrieve_relevant_chunks


def list_user_documents(
    db: Session,
    user_id: int,
) -> list[dict]:

    documents = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "created_at": document.created_at.isoformat(),
        }
        for document in documents
    ]


def search_documents(
    db: Session,
    user_id: int,
    query: str,
) -> list[dict]:

    return retrieve_relevant_chunks(
        query=query,
        n_results=5,
        user_id=user_id,
    )