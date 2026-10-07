from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Batch(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str = Field(default="Batch Upload")
    status: str = Field(default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    total_files: int = Field(default=0)
    processed_files: int = Field(default=0)
    total_at_risk_inr: float = Field(default=0.0)
    matched_count: int = Field(default=0)
    review_count: int = Field(default=0)
    mismatch_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    documents: List["Document"] = Relationship(back_populates="batch", cascade_delete=True)
    match_sets: List["MatchSet"] = Relationship(back_populates="batch", cascade_delete=True)

class Document(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    batch_id: str = Field(foreign_key="batch.id", index=True)
    match_set_id: Optional[str] = Field(default=None, foreign_key="matchset.id", nullable=True, index=True)
    filename: str
    file_path: str
    file_hash: str = Field(index=True)
    doc_type: str = Field(default="UNKNOWN")  # PO, INVOICE, GRN, UNKNOWN
    page_count: int = Field(default=1)
    status: str = Field(default="UPLOADED")  # UPLOADED, CLASSIFIED, EXTRACTED, FAILED
    error_message: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    batch: Optional[Batch] = Relationship(back_populates="documents")
    extracted_doc: Optional["ExtractedDoc"] = Relationship(back_populates="document", cascade_delete=True)
    line_items: List["LineItem"] = Relationship(back_populates="document", cascade_delete=True)

class ExtractedDoc(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    document_id: str = Field(foreign_key="document.id", unique=True, index=True)
    doc_type: str
    doc_number: Optional[str] = Field(default=None, nullable=True)
    doc_date: Optional[str] = Field(default=None, nullable=True)
    po_reference: Optional[str] = Field(default=None, nullable=True)
    supplier_name: Optional[str] = Field(default=None, nullable=True)
    supplier_gstin: Optional[str] = Field(default=None, nullable=True)
    buyer_name: Optional[str] = Field(default=None, nullable=True)
    buyer_gstin: Optional[str] = Field(default=None, nullable=True)
    place_of_supply: Optional[str] = Field(default=None, nullable=True)
    supplier_state_code: Optional[str] = Field(default=None, nullable=True)
    buyer_state_code: Optional[str] = Field(default=None, nullable=True)
    currency: str = Field(default="INR")
    vehicle_number: Optional[str] = Field(default=None, nullable=True)
    eway_bill_number: Optional[str] = Field(default=None, nullable=True)
    taxable_total: float = Field(default=0.0)
    cgst_total: float = Field(default=0.0)
    sgst_total: float = Field(default=0.0)
    igst_total: float = Field(default=0.0)
    round_off: float = Field(default=0.0)
    grand_total: float = Field(default=0.0)
    amount_in_words: Optional[str] = Field(default=None, nullable=True)
    raw_json: str = Field(default="{}")
    confidence_json: str = Field(default="{}")
    bounding_boxes_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    document: Optional[Document] = Relationship(back_populates="extracted_doc")
