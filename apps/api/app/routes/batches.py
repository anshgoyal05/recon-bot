import os
import shutil
import zipfile
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import json

from app.models.database import engine
from app.models.batch import Batch, Document
from app.models.match import MatchSet
from app.services.ingestion import (
    process_batch_files,
    get_progress_queue,
    remove_progress_queue,
    broadcast_progress
)
from app.services.exporter import export_batch_excel
from app.config import settings

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.post("")
async def upload_batch(
    background_tasks: BackgroundTasks,
    name: Optional[str] = Form("Reconciliation Batch"),
    files: List[UploadFile] = File(...),
):
    """
    Accepts folder upload (webkitdirectory), multi-PDF upload, or ZIP file.
    Creates a new batch and launches background processing.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    with Session(engine) as session:
        batch = Batch(name=name or "Batch Upload", status="PENDING")
        session.add(batch)
        session.commit()
        session.refresh(batch)
        batch_id = batch.id

    batch_dir = settings.STORAGE_DIR / "uploads" / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    for file in files:
        filename = file.filename or "uploaded_file"
        file_path = batch_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Handle ZIP file
        if filename.lower().endswith(".zip"):
            extract_dir = batch_dir / "unzipped"
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

    # Launch background processing
    background_tasks.add_task(process_batch_files, batch_id, batch_dir)

    return {
        "batch_id": batch_id,
        "name": name,
        "status": "PROCESSING",
        "message": f"Upload accepted with {len(files)} items. Processing started.",
    }

@router.post("/demo")
async def load_demo_batch(background_tasks: BackgroundTasks):
    """
    1-Click Demo: copies bundled sample PDFs to a new batch and reconciles them.
    """
    with Session(engine) as session:
        batch = Batch(name="MSME Auto-Parts Demo Batch", status="PENDING")
        session.add(batch)
        session.commit()
        session.refresh(batch)
        batch_id = batch.id

    batch_dir = settings.STORAGE_DIR / "uploads" / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Copy bundled sample PDFs from sample_data/sets/
    sample_sets_dir = settings.SAMPLE_DATA_DIR / "sets"
    if sample_sets_dir.exists():
        for pdf_file in sample_sets_dir.rglob("*.pdf"):
            dest_file = batch_dir / pdf_file.name
            shutil.copy2(pdf_file, dest_file)

    background_tasks.add_task(process_batch_files, batch_id, batch_dir)

    return {
        "batch_id": batch_id,
        "name": "MSME Auto-Parts Demo Batch",
        "status": "PROCESSING",
        "message": "Demo data loaded. Processing started.",
    }

@router.get("")
def list_batches():
    with Session(engine) as session:
        batches = session.exec(select(Batch).order_by(Batch.created_at.desc())).all()
        return batches

@router.get("/{batch_id}")
def get_batch(batch_id: str):
    with Session(engine) as session:
        batch = session.get(Batch, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        return batch

@router.get("/{batch_id}/progress")
async def stream_batch_progress(batch_id: str):
    """
    Server-Sent Events (SSE) stream providing real-time file-by-file progress updates.
    """
    queue = get_progress_queue(batch_id)

    async def event_generator():
        try:
            # Yield initial status
            with Session(engine) as session:
                b = session.get(Batch, batch_id)
                if b:
                    init_data = {
                        "status": b.status,
                        "processed": b.processed_files,
                        "total": b.total_files,
                        "total_at_risk_inr": b.total_at_risk_inr,
                        "matched": b.matched_count,
                        "review": b.review_count,
                        "mismatch": b.mismatch_count,
                    }
                    yield f"data: {json.dumps(init_data)}\n\n"

            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ("COMPLETED", "FAILED"):
                    break
        finally:
            remove_progress_queue(batch_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.get("/{batch_id}/export.xlsx")
def download_excel(batch_id: str):
    stream = export_batch_excel(batch_id)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=Recon_Bot_Batch_{batch_id[:8]}.xlsx"
        }
    )
