from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

class HsnRate(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    hsn_code: str = Field(index=True)
    description: str
    rate_percent: float  # e.g. 18.0, 12.0, 28.0, 5.0, 0.0
    effective_from: str  # YYYY-MM-DD
    effective_to: Optional[str] = Field(default=None, nullable=True)  # YYYY-MM-DD or None for current
    category: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Supplier(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str
    gstin: str = Field(index=True)
    state_code: str
    state_name: str
    email: Optional[str] = Field(default=None, nullable=True)
    phone: Optional[str] = Field(default=None, nullable=True)
    payment_terms_days: int = Field(default=30)
    is_verified: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SystemSettings(SQLModel, table=True):
    id: str = Field(default="default", primary_key=True)
    company_name: str = Field(default="Precision Auto Components Pvt Ltd")
    company_gstin: str = Field(default="27AAACP1234M1Z5")
    company_state_code: str = Field(default="27")
    company_state: str = Field(default="Maharashtra")
    qty_tolerance_pct: float = Field(default=2.0)
    price_tolerance_inr: float = Field(default=0.01)
    price_tolerance_pct: float = Field(default=0.5)
    tax_roundoff_tolerance_inr: float = Field(default=1.0)
    gemini_api_key_configured: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
