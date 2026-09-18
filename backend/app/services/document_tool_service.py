from sqlalchemy.orm import Session

from backend.app.models.document import Document


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