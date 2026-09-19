from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import get_current_user, get_db
from backend.app.schemas.document import DocumentResponse
from backend.app.services.document_service import (
    create_document,
    get_user_documents,
    get_user_document,
    delete_document,
)
from backend.app.services.document_extraction_service import extract_text
from backend.app.services.chunking_service import chunk_text
from backend.app.services.document_chunk_service import (
    create_document_chunks,
    delete_document_chunks,
)
from backend.app.services.chroma_service import (
    add_document_chunk,
    delete_document_chunks as delete_chroma_chunks,
)


router = APIRouter(prefix="/documents", tags=["Documents"])


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    file_path = UPLOAD_DIR / file.filename

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        document = create_document(
            db=db,
            user_id=int(current_user["sub"]),
            filename=file.filename,
            file_type=file.content_type or "unknown",
            file_path=str(file_path),
        )

        text = extract_text(
            str(file_path),
            file.content_type or "unknown",
        )

        chunks = chunk_text(text)

        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        for index, chunk in enumerate(chunks):
            add_document_chunk(
                chunk_id=f"{document.id}_{index}",
                text=chunk,
                document_id=document.id,
                chunk_index=index,
                user_id=int(current_user["sub"]),
            )

        return document

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {error}",
        )


@router.get("", response_model=list[DocumentResponse])
def get_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_documents(
        db=db,
        user_id=int(current_user["sub"]),
    )


@router.delete("/{document_id}")
def delete_user_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    document = get_user_document(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        # 1. Delete chunks from Chroma
        delete_chroma_chunks(document.id)

        # 2. Delete chunks from PostgreSQL
        delete_document_chunks(
            db=db,
            document_id=document.id,
        )

        # 3. Delete uploaded file
        file_path = Path(document.file_path)

        if file_path.exists():
            file_path.unlink()

        # 4. Delete document metadata from PostgreSQL
        delete_document(
            db=db,
            document=document,
        )

        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {error}",
        )