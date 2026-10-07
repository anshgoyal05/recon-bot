from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from app.models.database import engine
from app.models.master import HsnRate, Supplier, SystemSettings
from app.config import settings

router = APIRouter(tags=["Masters & Settings"])

# =============================================================================
# Settings
# =============================================================================
class UpdateSettingsRequest(BaseModel):
    company_name: Optional[str] = None
    company_gstin: Optional[str] = None
    company_state_code: Optional[str] = None
    qty_tolerance_pct: Optional[float] = None
    price_tolerance_inr: Optional[float] = None
    price_tolerance_pct: Optional[float] = None
    tax_roundoff_tolerance_inr: Optional[float] = None

@router.get("/settings")
def get_settings():
    with Session(engine) as session:
        s = session.get(SystemSettings, "default")
        if not s:
            s = SystemSettings(id="default")
            session.add(s)
            session.commit()
            session.refresh(s)
        s.gemini_api_key_configured = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5)
        return s

@router.patch("/settings")
def update_settings(payload: UpdateSettingsRequest):
    with Session(engine) as session:
        s = session.get(SystemSettings, "default")
        if not s:
            s = SystemSettings(id="default")

        if payload.company_name is not None:
            s.company_name = payload.company_name
        if payload.company_gstin is not None:
            s.company_gstin = payload.company_gstin
        if payload.company_state_code is not None:
            s.company_state_code = payload.company_state_code
        if payload.qty_tolerance_pct is not None:
            s.qty_tolerance_pct = payload.qty_tolerance_pct
        if payload.price_tolerance_inr is not None:
            s.price_tolerance_inr = payload.price_tolerance_inr
        if payload.price_tolerance_pct is not None:
            s.price_tolerance_pct = payload.price_tolerance_pct
        if payload.tax_roundoff_tolerance_inr is not None:
            s.tax_roundoff_tolerance_inr = payload.tax_roundoff_tolerance_inr

        s.updated_at = datetime.now(timezone.utc)
        session.add(s)
        session.commit()
        session.refresh(s)
        return s

# =============================================================================
# HSN Rates CRUD
# =============================================================================
class HsnRateCreate(BaseModel):
    hsn_code: str
    description: str
    rate_percent: float
    effective_from: str
    effective_to: Optional[str] = None
    category: Optional[str] = None

@router.get("/hsn-rates")
def list_hsn_rates():
    with Session(engine) as session:
        return session.exec(select(HsnRate).order_by(HsnRate.hsn_code, HsnRate.effective_from.desc())).all()

@router.post("/hsn-rates")
def create_hsn_rate(payload: HsnRateCreate):
    with Session(engine) as session:
        rate = HsnRate(
            hsn_code=payload.hsn_code.strip(),
            description=payload.description.strip(),
            rate_percent=payload.rate_percent,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            category=payload.category,
        )
        session.add(rate)
        session.commit()
        session.refresh(rate)
        return rate

@router.put("/hsn-rates/{rate_id}")
def update_hsn_rate(rate_id: str, payload: HsnRateCreate):
    with Session(engine) as session:
        rate = session.get(HsnRate, rate_id)
        if not rate:
            raise HTTPException(status_code=404, detail="HSN Rate not found")
        rate.hsn_code = payload.hsn_code.strip()
        rate.description = payload.description.strip()
        rate.rate_percent = payload.rate_percent
        rate.effective_from = payload.effective_from
        rate.effective_to = payload.effective_to
        rate.category = payload.category
        session.add(rate)
        session.commit()
        session.refresh(rate)
        return rate

@router.delete("/hsn-rates/{rate_id}")
def delete_hsn_rate(rate_id: str):
    with Session(engine) as session:
        rate = session.get(HsnRate, rate_id)
        if not rate:
            raise HTTPException(status_code=404, detail="HSN Rate not found")
        session.delete(rate)
        session.commit()
        return {"status": "DELETED", "id": rate_id}

# =============================================================================
# Suppliers CRUD
# =============================================================================
class SupplierCreate(BaseModel):
    name: str
    gstin: str
    state_code: str
    state_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

@router.get("/suppliers")
def list_suppliers():
    with Session(engine) as session:
        return session.exec(select(Supplier).order_by(Supplier.name)).all()

@router.post("/suppliers")
def create_supplier(payload: SupplierCreate):
    with Session(engine) as session:
        sup = Supplier(
            name=payload.name,
            gstin=payload.gstin,
            state_code=payload.state_code,
            state_name=payload.state_name,
            email=payload.email,
            phone=payload.phone,
        )
        session.add(sup)
        session.commit()
        session.refresh(sup)
        return sup
