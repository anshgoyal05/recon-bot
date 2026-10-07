from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BoundingBox(BaseModel):
    # Normalized coordinates in [0, 1000] space
    ymin: int = Field(default=0, ge=0, le=1000)
    xmin: int = Field(default=0, ge=0, le=1000)
    ymax: int = Field(default=1000, ge=0, le=1000)
    xmax: int = Field(default=1000, ge=0, le=1000)
    page_number: int = Field(default=1, ge=1)

class FieldWithConfidence(BaseModel):
    value: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None

class ExtractedLineItem(BaseModel):
    serial_no: int = Field(default=1)
    description: str
    hsn_sac: Optional[str] = None
    quantity: float
    uom: str = "PCS"
    unit_price: float
    discount: float = 0.0
    taxable_value: float
    cgst_rate: float = 0.0
    cgst_amount: float = 0.0
    sgst_rate: float = 0.0
    sgst_amount: float = 0.0
    igst_rate: float = 0.0
    igst_amount: float = 0.0
    cess: float = 0.0
    line_total: float
    confidence: float = Field(default=0.98, ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None
    page_number: int = 1

class ExtractedDocumentData(BaseModel):
    document_type: str = Field(description="One of: PURCHASE_ORDER, INVOICE, GOODS_RECEIPT_NOTE")
    document_number: Optional[str] = None
    document_date: Optional[str] = Field(default=None, description="ISO Date YYYY-MM-DD")
    po_reference: Optional[str] = Field(default=None, description="PO number referenced on the document, if any")

    supplier_name: Optional[str] = None
    supplier_gstin: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None
    supplier_state_code: Optional[str] = None
    buyer_state_code: Optional[str] = None

    currency: str = "INR"
    vehicle_number: Optional[str] = None
    eway_bill_number: Optional[str] = None

    line_items: List[ExtractedLineItem] = Field(default_factory=list)

    taxable_total: float = 0.0
    cgst_total: float = 0.0
    sgst_total: float = 0.0
    igst_total: float = 0.0
    round_off: float = 0.0
    grand_total: float = 0.0
    amount_in_words: Optional[str] = None

    field_confidences: Dict[str, float] = Field(default_factory=dict)
    field_bboxes: Dict[str, BoundingBox] = Field(default_factory=dict)
