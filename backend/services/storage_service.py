import os
import re
import uuid

from supabase import create_client, Client

BUCKET_NAME = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")
TABLE_NAME = "documents"


def _get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    return create_client(url, key)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:50].strip("-")


def save_document(
    title: str,
    document_type: str,
    topic: str,
    style: str,
    content: str,
    user_id: str | None = None,
) -> dict:
    client = _get_client()

    slug = _slugify(title)
    unique_suffix = str(uuid.uuid4())[:8]
    file_name = f"{slug}_{unique_suffix}.md"

    file_bytes = content.encode("utf-8")

    client.storage.from_(BUCKET_NAME).upload(
        path=file_name,
        file=file_bytes,
        file_options={"content-type": "text/markdown; charset=utf-8"},
    )

    storage_url = client.storage.from_(BUCKET_NAME).get_public_url(file_name)

    record = {
        "user_id": user_id,
        "title": title,
        "document_type": document_type,
        "topic": topic,
        "style": style,
        "file_name": file_name,
        "storage_url": storage_url,
        "file_size": len(file_bytes),
    }

    result = client.table(TABLE_NAME).insert(record).execute()
    return result.data[0]
