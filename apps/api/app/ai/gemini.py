import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.ai.provider import LLMProvider
from app.ai.schemas import ExtractedDocumentData
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT, REPAIR_PROMPT, EMAIL_SYSTEM_PROMPT
from app.config import settings
from app.ai.mock import MockProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.mock_fallback = MockProvider()
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def extract_document(
        self,
        pdf_path: str,
        rendered_images: List[Dict[str, Any]],
        filename: str = "",
        file_hash: str = "",
    ) -> ExtractedDocumentData:
        if not self.api_key or not self.model:
            return await self.mock_fallback.extract_document(
                pdf_path, rendered_images, filename, file_hash
            )

        try:
            # Prepare image parts for Gemini
            image_parts = []
            for img_info in rendered_images[:5]:  # limit to first 5 pages for extraction efficiency
                img_path = img_info["image_path"]
                with open(img_path, "rb") as f:
                    image_parts.append({
                        "mime_type": "image/png",
                        "data": f.read()
                    })

            prompt = (
                f"{EXTRACTION_SYSTEM_PROMPT}\n\n"
                f"Filename: {filename}\n"
                f"Extract all information into the required JSON schema structure."
            )

            contents = [prompt] + image_parts
            response = self.model.generate_content(
                contents,
                generation_config={"response_mime_type": "application/json"}
            )

            text_output = response.text.strip()
            if text_output.startswith("```json"):
                text_output = text_output.removeprefix("```json").removesuffix("```").strip()

            try:
                data = json.loads(text_output)
                return ExtractedDocumentData.model_validate(data)
            except Exception as parse_err:
                # Retry repair once
                repair_prompt = REPAIR_PROMPT.format(error_message=str(parse_err))
                repair_response = self.model.generate_content(
                    [repair_prompt, text_output],
                    generation_config={"response_mime_type": "application/json"}
                )
                repaired_text = repair_response.text.strip()
                if repaired_text.startswith("```json"):
                    repaired_text = repaired_text.removeprefix("```json").removesuffix("```").strip()
                data = json.loads(repaired_text)
                return ExtractedDocumentData.model_validate(data)

        except Exception as e:
            # Fall back to mock provider gracefully
            print(f"[GeminiProvider Error] {e}. Falling back to MockProvider.")
            return await self.mock_fallback.extract_document(
                pdf_path, rendered_images, filename, file_hash
            )

    async def generate_dispute_email(
        self,
        supplier_name: str,
        supplier_gstin: str,
        po_number: str,
        invoice_number: str,
        discrepancies: List[Dict[str, Any]],
        total_at_risk_inr: float,
    ) -> str:
        if not self.api_key or not self.model:
            return await self.mock_fallback.generate_dispute_email(
                supplier_name, supplier_gstin, po_number, invoice_number, discrepancies, total_at_risk_inr
            )

        try:
            issues_json = json.dumps(discrepancies, indent=2)
            prompt = (
                f"{EMAIL_SYSTEM_PROMPT}\n\n"
                f"Buyer: {settings.COMPANY_NAME} (GSTIN: {settings.COMPANY_GSTIN})\n"
                f"Supplier: {supplier_name} (GSTIN: {supplier_gstin})\n"
                f"PO Number: {po_number}\n"
                f"Invoice Number: {invoice_number}\n"
                f"Total Rupee Amount at Risk: ₹{total_at_risk_inr:,.2f}\n"
                f"Identified Discrepancies:\n{issues_json}\n\n"
                f"Draft a formal, itemized dispute email to the supplier."
            )
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return await self.mock_fallback.generate_dispute_email(
                supplier_name, supplier_gstin, po_number, invoice_number, discrepancies, total_at_risk_inr
            )
