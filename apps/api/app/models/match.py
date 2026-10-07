from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

class MatchSet(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    batch_id: str = Field(foreign_key="batch.id", index=True)
    set_name: str
    po_document_id: Optional[str] = Field(default=None, nullable=True)
    invoice_document_id: Optional[str] = Field(default=None, nullable=True)
    grn_document_id: Optional[str] = Field(default=None, nullable=True)
    po_number: Optional[str] = Field(default=None, nullable=True)
    invoice_number: Optional[str] = Field(default=None, nullable=True)
    grn_number: Optional[str] = Field(default=None, nullable=True)
    supplier_name: Optional[str] = Field(default=None, nullable=True)
    supplier_gstin: Optional[str] = Field(default=None, nullable=True)
    grouping_method: str = Field(default="PO_REFERENCE")  # PO_REFERENCE, GSTIN_DATE, FUZZY_LINE, MANUAL
    grouping_confidence: float = Field(default=1.0)
    verdict: str = Field(default="REVIEW")  # MATCHED, REVIEW, MISMATCH
    total_at_risk_inr: float = Field(default=0.0)
    status: str = Field(default="UNRESOLVED")  # UNRESOLVED, RESOLVED, DISPUTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    batch: Optional["Batch"] = Relationship(back_populates="match_sets")
    line_items: List["LineItem"] = Relationship(back_populates="match_set", cascade_delete=True)
    discrepancies: List["Discrepancy"] = Relationship(back_populates="match_set", cascade_delete=True)
    audit_logs: List["AuditLog"] = Relationship(back_populates="match_set", cascade_delete=True)

class LineItem(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    match_set_id: Optional[str] = Field(default=None, foreign_key="matchset.id", nullable=True, index=True)
    doc_type: str = Field(default="INVOICE")  # PO, INVOICE, GRN
    line_number: int = Field(default=1)
    description: str
    hsn_sac: Optional[str] = Field(default=None, nullable=True)
    quantity: float = Field(default=0.0)
    uom: str = Field(default="PCS")
    unit_price: float = Field(default=0.0)
    discount: float = Field(default=0.0)
    taxable_value: float = Field(default=0.0)
    cgst_rate: float = Field(default=0.0)
    cgst_amount: float = Field(default=0.0)
    sgst_rate: float = Field(default=0.0)
    sgst_amount: float = Field(default=0.0)
    igst_rate: float = Field(default=0.0)
    igst_amount: float = Field(default=0.0)
    cess_amount: float = Field(default=0.0)
    line_total: float = Field(default=0.0)
    bbox_json: Optional[str] = Field(default=None, nullable=True)
    confidence: float = Field(default=1.0)
    page_number: int = Field(default=1)

    document: Optional["Document"] = Relationship(back_populates="line_items")
    match_set: Optional[MatchSet] = Relationship(back_populates="line_items")

class Discrepancy(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    match_set_id: str = Field(foreign_key="matchset.id", index=True)
    line_item_id: Optional[str] = Field(default=None, nullable=True)
    document_id: Optional[str] = Field(default=None, nullable=True)
    page_number: int = Field(default=1)
    discrepancy_type: str  # QUANTITY, UNIT_PRICE, TAX_GST, ARITHMETIC, DUPLICATE, HEADER
    severity: str = Field(default="ERROR")  # ERROR, WARNING, INFO
    field_name: str
    expected_value: str = Field(default="")
    actual_value: str = Field(default="")
    impact_inr: float = Field(default=0.0)
    explanation: str = Field(default="")
    status: str = Field(default="OPEN")  # OPEN, ACCEPTED, DISPUTED, RESOLVED
    user_note: Optional[str] = Field(default=None, nullable=True)
    bbox_json: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    match_set: Optional[MatchSet] = Relationship(back_populates="discrepancies")

class AuditLog(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    match_set_id: Optional[str] = Field(default=None, foreign_key="matchset.id", nullable=True, index=True)
    discrepancy_id: Optional[str] = Field(default=None, nullable=True)
    action: str  # CREATED, ACCEPTED, DISPUTED, RESOLVED, REGROUPED, NOTE_ADDED, EMAIL_GENERATED
    previous_state: Optional[str] = Field(default=None, nullable=True)
    new_state: Optional[str] = Field(default=None, nullable=True)
    details: str
    user_name: str = Field(default="Auditor")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    match_set: Optional[MatchSet] = Relationship(back_populates="audit_logs")
