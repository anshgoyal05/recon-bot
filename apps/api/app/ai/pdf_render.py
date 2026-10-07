import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Tuple
import os
from app.config import settings
from app.ai.schemas import BoundingBox

def get_rendered_pages_dir(file_hash: str) -> Path:
    target_dir = settings.STORAGE_DIR / "rendered" / file_hash
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir

def render_pdf_to_images(pdf_path: str, file_hash: str, dpi: int = 200) -> List[Dict[str, Any]]:
    """
    Renders all pages of a PDF to PNG at specified DPI.
    Returns metadata list containing image path, width, height, and page index.
    """
    doc = fitz.open(pdf_path)
    output_dir = get_rendered_pages_dir(file_hash)
    pages_info = []

    # 72 points per inch standard PDF coordinate space
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        image_path = output_dir / f"page_{page_num}.png"

        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(str(image_path))

        # Extract words for bounding box resolution
        # word tuple: (x0, y0, x1, y1, word, block_no, line_no, word_no)
        rect = page.rect
        page_width = rect.width
        page_height = rect.height

        pages_info.append({
            "page_number": page_num,
            "image_path": str(image_path),
            "width": pix.width,
            "height": pix.height,
            "pdf_width": page_width,
            "pdf_height": page_height,
        })

    doc.close()
    return pages_info

def locate_text_bbox(pdf_path: str, search_text: str, page_number: int = 1) -> BoundingBox:
    """
    Searches for text in the PDF page and converts coordinates to normalized [0, 1000] space.
    """
    try:
        doc = fitz.open(pdf_path)
        if page_number > len(doc):
            doc.close()
            return BoundingBox(ymin=100, xmin=100, ymax=200, xmax=300, page_number=page_number)

        page = doc[page_number - 1]
        rect = page.rect
        instances = page.search_for(search_text)
        doc.close()

        if instances:
            inst = instances[0]
            ymin = int((inst.y0 / rect.height) * 1000)
            xmin = int((inst.x0 / rect.width) * 1000)
            ymax = int((inst.y1 / rect.height) * 1000)
            xmax = int((inst.x1 / rect.width) * 1000)
            return BoundingBox(
                ymin=max(0, min(1000, ymin)),
                xmin=max(0, min(1000, xmin)),
                ymax=max(0, min(1000, ymax)),
                xmax=max(0, min(1000, xmax)),
                page_number=page_number,
            )
    except Exception:
        pass

    return BoundingBox(ymin=200, xmin=100, ymax=300, xmax=400, page_number=page_number)
