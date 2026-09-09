from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import get_current_user, get_db
from backend.app.schemas.document import DocumentResponse
from backend.app.services.document_service import (
    create_document,
    get_user_documents,
)
from backend.app.services.document_extraction_service import extract_text
from backend.app.services.chunking_service import chunk_text
from backend.app.services.document_chunk_service import create_document_chunks
from backend.app.services.chroma_service import add_document_chunk


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
        # 1. Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # 2. Save document metadata
        document = create_document(
            db=db,
            user_id=int(current_user["sub"]),
            filename=file.filename,
            file_type=file.content_type or "unknown",
            file_path=str(file_path),
        )

        # 3. Extract text
        text = extract_text(
            str(file_path),
            file.content_type or "unknown",
        )

        # 4. Split extracted text into chunks
        chunks = chunk_text(text)

        # 5. Save chunks in PostgreSQL
        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        # 6. Generate embeddings and store chunks in Chroma
        for index, chunk in enumerate(chunks):
            add_document_chunk(
                chunk_id=f"{document.id}_{index}",
                text=chunk,
                document_id=document.id,
                chunk_index=index,
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
    documents = get_user_documents(
        db=db,
        user_id=int(current_user["sub"]),
    )

    return documents