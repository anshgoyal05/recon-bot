import json
from pathlib import Path
import pytest
from app.config import settings
from app.ai.mock import MockProvider
from app.engine.reconciler import reconcile_match_set
from app.services.seed import seed_database

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

@pytest.mark.asyncio
async def test_all_sample_sets_match_ground_truth():
    ground_truth_path = SAMPLE_DATA_DIR / "ground_truth.json"
    assert ground_truth_path.exists(), "ground_truth.json must exist"

    with open(ground_truth_path, "r") as f:
        gt = json.load(f)

    mock_provider = MockProvider()
    processed_invoices_history = []

    for expected_set in gt["sets"]:
        set_id = expected_set["id"]
        po_file = SAMPLE_DATA_DIR / "sets" / expected_set["po_file"]
        inv_file = SAMPLE_DATA_DIR / "sets" / expected_set["invoice_file"]
        grn_file = SAMPLE_DATA_DIR / "sets" / expected_set["grn_file"]

        # Extract documents
        po_doc = await mock_provider.extract_document(str(po_file), [], po_file.name, po_file.stem)
        inv_doc = await mock_provider.extract_document(str(inv_file), [], inv_file.name, inv_file.stem)
        grn_doc = await mock_provider.extract_document(str(grn_file), [], grn_file.name, grn_file.stem)

        # Run reconciliation
        result = reconcile_match_set(
            po_doc=po_doc,
            invoice_doc=inv_doc,
            grn_doc=grn_doc,
            existing_invoices=processed_invoices_history,
            match_set_id=set_id,
        )

        # Record invoice for duplicate detection in subsequent sets
        processed_invoices_history.append({
            "match_set_id": set_id,
            "set_name": expected_set["set_name"],
            "supplier_gstin": inv_doc.supplier_gstin,
            "invoice_number": inv_doc.document_number,
            "grand_total": inv_doc.grand_total,
            "invoice_date": inv_doc.document_date,
        })

        # Assert verdict matches ground truth
        expected_verdict = expected_set["expected_verdict"]
        assert result.verdict == expected_verdict, (
            f"Set {set_id} expected verdict {expected_verdict}, got {result.verdict}. "
            f"Discrepancies found: {[d['explanation'] for d in result.discrepancies]}"
        )

        # If clean set, assert 0 errors and 0 risk
        if expected_verdict == "MATCHED":
            assert result.error_count == 0
            assert result.total_at_risk_inr == 0.0

        # If mismatch set, assert that the expected discrepancy type was caught!
        if expected_verdict == "MISMATCH":
            assert result.error_count > 0
            assert result.total_at_risk_inr > 0.0

            for exp_d in expected_set["expected_discrepancies"]:
                expected_type = exp_d["type"]
                # Verify that at least one discrepancy of this type was detected
                matched = any(d["discrepancy_type"] == expected_type for d in result.discrepancies)
                assert matched, (
                    f"Set {set_id} expected discrepancy of type {expected_type}, but found types: "
                    f"{[d['discrepancy_type'] for d in result.discrepancies]}"
                )
