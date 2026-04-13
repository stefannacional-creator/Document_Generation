import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from services.agent_service import DocumentAgentService
from services.pdf_service import markdown_to_pdf
from services.storage_service import save_document

router = APIRouter()


class GenerateRequest(BaseModel):
    title: str
    document_type: str
    topic: str
    style: Optional[str] = "professional"
    additional_instructions: Optional[str] = None
    reference_content: Optional[str] = None  # extracted text from uploaded file


class SaveRequest(BaseModel):
    title: str
    document_type: str
    topic: str
    style: Optional[str] = "professional"
    content: str
    user_id: Optional[str] = None


class PdfRequest(BaseModel):
    markdown: str
    filename: Optional[str] = "document"


@router.post("/stream")
async def generate_document_stream(request: GenerateRequest):
    """
    SSE endpoint — streams agent events as the document is built.
    Event shapes:
      {"type": "tool_call",       "name": str, "args": dict}
      {"type": "outline_planned", "sections": list}
      {"type": "section_written", "section_id": str, "heading": str}
      {"type": "tool_result",     "name": str, "result": str}
      {"type": "complete",        "document": str}
      {"type": "error",           "message": str}
    """
    service = DocumentAgentService()

    async def event_stream():
        try:
            async for event in service.generate(
                title=request.title,
                document_type=request.document_type,
                topic=request.topic,
                style=request.style or "professional",
                additional_instructions=request.additional_instructions,
                reference_content=request.reference_content,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/save")
def save_document_endpoint(request: SaveRequest):
    """Save generated markdown to Supabase Storage and record metadata in the DB."""
    try:
        record = save_document(
            title=request.title,
            document_type=request.document_type,
            topic=request.topic,
            style=request.style or "professional",
            content=request.content,
            user_id=request.user_id,
        )
        return record
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/pdf")
def download_pdf(request: PdfRequest):
    """Convert generated Markdown to a styled PDF and return it as a download."""
    pdf_bytes = markdown_to_pdf(request.markdown)
    safe_name = "".join(c for c in request.filename if c.isalnum() or c in " -_") or "document"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}.pdf"',
        },
    )
