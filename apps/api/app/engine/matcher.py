from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz
from app.ai.schemas import ExtractedLineItem

class MatchedLineTriplet:
    def __init__(
        self,
        po_item: Optional[ExtractedLineItem] = None,
        invoice_item: Optional[ExtractedLineItem] = None,
        grn_item: Optional[ExtractedLineItem] = None,
        score: float = 1.0,
    ):
        self.po_item = po_item
        self.invoice_item = invoice_item
        self.grn_item = grn_item
        self.score = score

def calculate_item_similarity(
    item_a: ExtractedLineItem,
    item_b: ExtractedLineItem
) -> float:
    """
    Computes a composite similarity score [0.0 to 1.0] based on:
    - Fuzzy description similarity (rapidfuzz token_set_ratio)
    - HSN/SAC match (strong weight)
    - Quantity proximity
    """
    desc_sim = fuzz.token_set_ratio(item_a.description.lower(), item_b.description.lower()) / 100.0

    # HSN match bonus
    hsn_sim = 0.5
    if item_a.hsn_sac and item_b.hsn_sac:
        clean_a = str(item_a.hsn_sac).strip()
        clean_b = str(item_b.hsn_sac).strip()
        if clean_a == clean_b:
            hsn_sim = 1.0
        elif clean_a[:4] == clean_b[:4]:
            hsn_sim = 0.85
        else:
            hsn_sim = 0.0

    # Quantity proximity
    qty_sim = 0.5
    if item_a.quantity > 0 and item_b.quantity > 0:
        ratio = min(item_a.quantity, item_b.quantity) / max(item_a.quantity, item_b.quantity)
        qty_sim = ratio

    # Weighted composite score
    total_score = (desc_sim * 0.50) + (hsn_sim * 0.35) + (qty_sim * 0.15)
    return total_score

def match_lines_three_way(
    po_lines: List[ExtractedLineItem],
    invoice_lines: List[ExtractedLineItem],
    grn_lines: List[ExtractedLineItem],
) -> List[MatchedLineTriplet]:
    """
    Matches line items across PO, Invoice, and GRN into triplets.
    Handles partial deliveries and differing order of line items.
    """
    matched_triplets: List[MatchedLineTriplet] = []
    used_po_indices = set()
    used_grn_indices = set()

    for inv_idx, inv_item in enumerate(invoice_lines):
        # 1. Find best matching PO item
        best_po_idx = None
        best_po_score = -1.0

        for po_idx, po_item in enumerate(po_lines):
            if po_idx in used_po_indices:
                continue
            score = calculate_item_similarity(inv_item, po_item)
            if score > best_po_score:
                best_po_score = score
                best_po_idx = po_idx

        matched_po = None
        if best_po_idx is not None and best_po_score >= 0.40:
            matched_po = po_lines[best_po_idx]
            used_po_indices.add(best_po_idx)

        # 2. Find best matching GRN item
        best_grn_idx = None
        best_grn_score = -1.0

        for grn_idx, grn_item in enumerate(grn_lines):
            if grn_idx in used_grn_indices:
                continue
            score = calculate_item_similarity(inv_item, grn_item)
            if score > best_grn_score:
                best_grn_score = score
                best_grn_idx = grn_idx

        matched_grn = None
        if best_grn_idx is not None and best_grn_score >= 0.40:
            matched_grn = grn_lines[best_grn_idx]
            used_grn_indices.add(best_grn_idx)

        composite_score = min(
            best_po_score if matched_po else 0.5,
            best_grn_score if matched_grn else 0.5
        )

        matched_triplets.append(
            MatchedLineTriplet(
                po_item=matched_po,
                invoice_item=inv_item,
                grn_item=matched_grn,
                score=composite_score
            )
        )

    # Any remaining PO lines not invoiced
    for po_idx, po_item in enumerate(po_lines):
        if po_idx not in used_po_indices:
            matched_triplets.append(
                MatchedLineTriplet(po_item=po_item, invoice_item=None, grn_item=None, score=0.0)
            )

    return matched_triplets
