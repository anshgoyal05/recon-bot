from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session
from pathlib import Path
from app.models.database import engine
from app.models.batch import Document
from app.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/{document_id}/page/{page_number}.png")
def get_rendered_page(document_id: str, page_number: int = 1):
    with Session(engine) as session:
        doc = session.get(Document, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        file_hash = doc.file_hash
        img_path = settings.STORAGE_DIR / "rendered" / file_hash / f"page_{page_number}.png"

        if not img_path.exists():
            # If not rendered yet, trigger rendering on demand
            from app.ai.pdf_render import render_pdf_to_images
            if Path(doc.file_path).exists():
                render_pdf_to_images(doc.file_path, file_hash, dpi=200)

        if not img_path.exists():
            raise HTTPException(status_code=404, detail=f"Page image {page_number} not found")

        return FileResponse(img_path, media_type="image/png")

@router.get("/{document_id}/pdf")
def get_raw_pdf(document_id: str):
    with Session(engine) as session:
        doc = session.get(Document, document_id)
        if not doc or not Path(doc.file_path).exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        return FileResponse(doc.file_path, media_type="application/pdf", filename=doc.filename)
