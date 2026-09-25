import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import get_current_user, get_db
from backend.app.core.config import SUPABASE_BUCKET
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
    delete_document_chunks as delete_qdrant_chunks,
)
from backend.app.services.supabase_storage import (
    delete_file,
    supabase,
)


router = APIRouter(prefix="/documents", tags=["Documents"])


def get_file_type(file: UploadFile) -> str:
    content_type = file.content_type or ""

    if content_type and content_type != "application/octet-stream":
        return content_type

    extension = os.path.splitext(file.filename or "")[1].lower()

    extension_to_mime = {
        ".pdf": "application/pdf",
        ".docx": (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".md": "text/markdown",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".jsx": "text/javascript",
        ".ts": "text/typescript",
        ".tsx": "text/typescript",
        ".html": "text/html",
        ".css": "text/css",
        ".r": "text/plain",
    }

    return extension_to_mime.get(
        extension,
        content_type or "application/octet-stream",
    )


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

    user_id = int(current_user["sub"])
    storage_path = f"{user_id}/{file.filename}"
    file_type = get_file_type(file)

    try:
        # 1. Read uploaded file
        file_bytes = file.file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        # 2. Upload original file to Supabase Storage
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            storage_path,
            file_bytes,
            {
                "content-type": file_type,
                "upsert": "true",
            },
        )

        # 3. Create temporary file for extraction
        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            # 4. Extract text
            text = extract_text(
                temp_path,
                file_type,
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # 5. Create chunks
        chunks = chunk_text(text)

        # 6. Create document metadata in PostgreSQL
        document = create_document(
            db=db,
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_path=storage_path,
        )

        # 7. Store chunks in PostgreSQL
        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        # 8. Store vectors in Qdrant
        for index, chunk in enumerate(chunks):
            add_document_chunk(
                chunk_id=f"{document.id}_{index}",
                text=chunk,
                document_id=document.id,
                chunk_index=index,
                user_id=user_id,
            )

        return document

    except HTTPException:
        raise

    except Exception as error:
        import traceback

        traceback.print_exc()

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
        # 1. Delete vectors from Qdrant
        delete_qdrant_chunks(document.id)

        # 2. Delete chunks from PostgreSQL
        delete_document_chunks(
            db=db,
            document_id=document.id,
        )

        # 3. Delete original file from Supabase Storage
        delete_file(document.file_path)

        # 4. Delete document metadata
        delete_document(
            db=db,
            document=document,
        )

        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
        }

    except Exception as error:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {error}",
        )