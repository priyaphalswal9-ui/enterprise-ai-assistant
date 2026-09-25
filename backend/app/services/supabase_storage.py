from supabase import create_client

from backend.app.core.config import (
    SUPABASE_BUCKET,
    SUPABASE_SECRET_KEY,
    SUPABASE_URL,
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


def upload_file(
    file_path: str,
    storage_path: str,
    content_type: str,
):
    with open(file_path, "rb") as file:
        return (
            supabase.storage
            .from_(SUPABASE_BUCKET)
            .upload(
                storage_path,
                file,
                {
                    "content-type": content_type,
                    "upsert": "true",
                },
            )
        )


def delete_file(storage_path: str):
    return (
        supabase.storage
        .from_(SUPABASE_BUCKET)
        .remove([storage_path])
    )


def list_files():
    return (
        supabase.storage
        .from_(SUPABASE_BUCKET)
        .list()
    )