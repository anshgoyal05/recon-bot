from typing import Optional, Tuple
from sqlmodel import Session, select
from app.models.master import HsnRate
from app.models.database import engine

def get_hsn_rate_by_date(
    hsn_code: Optional[str],
    doc_date: Optional[str],
    session: Optional[Session] = None
) -> Optional[Tuple[float, str]]:
    """
    Looks up statutory GST rate for an HSN code based on document date.
    Picks the versioned slab active on that date.
    Returns (rate_percent, description) or None.
    """
    if not hsn_code:
        return None

    clean_hsn = str(hsn_code).strip()
    target_date = doc_date or "2025-02-15"

    def _query_db(s: Session, code: str) -> Optional[HsnRate]:
        stmt = (
            select(HsnRate)
            .where(HsnRate.hsn_code == code)
            .where(HsnRate.effective_from <= target_date)
        )
        candidates = s.exec(stmt).all()
        # Filter for effective_to
        for cand in candidates:
            if not cand.effective_to or cand.effective_to >= target_date:
                return cand
        return None

    def _search(s: Session) -> Optional[Tuple[float, str]]:
        # Try full code
        match = _query_db(s, clean_hsn)
        if match:
            return match.rate_percent, match.description

        # Try 4-digit prefix if longer
        if len(clean_hsn) > 4:
            match = _query_db(s, clean_hsn[:4])
            if match:
                return match.rate_percent, match.description

        # Try 2-digit chapter
        if len(clean_hsn) > 2:
            match = _query_db(s, clean_hsn[:2])
            if match:
                return match.rate_percent, match.description

        return None

    if session:
        return _search(session)
    else:
        with Session(engine) as local_session:
            return _search(local_session)
