from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.ai.schemas import ExtractedDocumentData

class LLMProvider(ABC):
    @abstractmethod
    async def extract_document(
        self,
        pdf_path: str,
        rendered_images: List[Dict[str, Any]],
        filename: str = "",
        file_hash: str = "",
    ) -> ExtractedDocumentData:
        """
        Extract structured data from rendered PDF page images.
        """
        pass

    @abstractmethod
    async def generate_dispute_email(
        self,
        supplier_name: str,
        supplier_gstin: str,
        po_number: str,
        invoice_number: str,
        discrepancies: List[Dict[str, Any]],
        total_at_risk_inr: float,
    ) -> str:
        """
        Draft a polite, itemized supplier dispute email.
        """
        pass
