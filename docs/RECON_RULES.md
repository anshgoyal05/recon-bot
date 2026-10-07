# Recon-Bot: Reconciliation Rules & Statutory Specifications

This document defines the deterministic rules executed by the Recon-Bot reconciliation engine.

---

## 1. Summary of Rule Categories

| Category | Check | Default Tolerance | Severity | Statutory / Commercial Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Quantity** | Invoiced > Received (GRN) | 0% | `ERROR` | Overbilling for unreceived inventory. |
| **Quantity** | Received > Ordered (PO) | $\pm 2.0\%$ | `WARNING` | Supplier delivered excess without authorization. |
| **Quantity** | Short Delivery | $\pm 2.0\%$ | `WARNING` | Partial delivery requiring balance tracking. |
| **Unit Price** | Invoiced Price > PO Price | ₹0.01 or 0.5% | `ERROR` | Unauthorized price increase / price creep. |
| **Unit Price** | Unit of Measure (UoM) | Strict Match | `ERROR` | E.g. MT invoiced as KG or vice versa. |
| **GST / Tax** | GSTIN Checksum Check | Modulo-36 | `ERROR` | Invalid GSTIN blocks Input Tax Credit (ITC). |
| **GST / Tax** | Intra- vs Inter-State | Strict | `ERROR` | CGST Act Sec 16(2), IGST Act Sec 7 & 8. |
| **GST / Tax** | CGST $\ne$ SGST | ₹0.00 | `ERROR` | Statutory requirement: CGST and SGST must match exactly. |
| **GST / Tax** | Statutory HSN Slab Rate | By Date | `ERROR` | Rate check against statutory HSN master as of invoice date. |
| **GST / Tax** | Tax Arithmetic Recomputation | ₹1.00 | `ERROR` | Taxable Value $\times$ Rate $\ne$ Tax Amount. |
| **Arithmetic** | Line Item Math | ₹1.00 | `ERROR` | $(Qty \times Price) - Discount \ne Taxable Value$. |
| **Arithmetic** | Invoice Header Summation | ₹1.00 | `ERROR` | Sum of line totals $\ne$ Invoice Grand Total. |
| **Duplicate** | Duplicate Invoice Number | Strict | `ERROR` | Re-submission of previously processed invoice. |
| **Header** | Invoice Date < PO Date | 0 days | `ERROR` | Invoice issued prior to purchase order creation. |

---

## 2. Detailed Rule Specifications

### 2.1 Quantity Checks

1. **Short Received vs Invoiced:**
   - **Condition:** $\text{Invoiced Qty} > \text{Received Qty}$
   - **Formula for ₹ at Risk:**
     $$\text{Impact INR} = (\text{Invoiced Qty} - \text{Received Qty}) \times \text{Unit Price} \times (1 + \text{Tax Rate})$$
   - **Example:** Invoiced 100 pcs @ ₹800 + 18% GST; GRN confirms only 80 pcs received.
   - **Rupee Impact:** $(100 - 80) \times 800 \times 1.18 = \text{₹18,880.00}$.

2. **Excess Supply vs PO:**
   - **Condition:** $\text{Received Qty} > \text{Ordered Qty} \times (1 + \text{Tolerance})$.
   - **Verdict:** `REVIEW` (Warning). Flags shop-floor receiving of unauthorized excess quantity.

---

### 2.2 Unit Price Checks

1. **Price Creep / Rate Variance:**
   - **Condition:** $\text{Invoiced Unit Price} > \text{PO Unit Price} + \max(\text{Tol}_{\text{INR}}, \text{PO Price} \times \text{Tol}_{\%})$
   - **Formula for ₹ at Risk:**
     $$\text{Impact INR} = (\text{Invoiced Price} - \text{PO Price}) \times \text{Invoiced Qty} \times (1 + \text{Tax Rate})$$
   - **Example:** PO agreed price ₹120.00; Supplier invoiced at ₹145.00 for 500 pcs @ 18% GST.
   - **Rupee Impact:** $(145 - 120) \times 500 \times 1.18 = \text{₹14,750.00}$.

---

### 2.3 Statutory GST Intelligence

1. **GSTIN Validation & Modulo-36 Checksum:**
   - Formatted: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`
   - Positions 1-2: Valid Indian State/UT code ($01-38$, $97, 99$).
   - Position 15: Checksum calculated by Modulo-36 algorithm.
   - **Impact:** An invalid GSTIN guarantees rejection during GSTR-2B matching, blocking Input Tax Credit.

2. **Tax Classification (Intra-State vs Inter-State):**
   - **Intra-State:** $\text{Supplier State} = \text{Place of Supply}$.
     - Permitted Taxes: **CGST + SGST**.
     - Forbidden: IGST.
   - **Inter-State:** $\text{Supplier State} \ne \text{Place of Supply}$.
     - Permitted Taxes: **IGST**.
     - Forbidden: CGST, SGST.
   - **Rupee at Risk:** 100% of the incorrectly charged tax amount, as Section 16(2) of the CGST Act forbids claiming ITC for taxes collected under the wrong head.

3. **Dynamic HSN Statutory Rate Lookup:**
   - Rates are keyed by `(HSN, Effective Date Range)`.
   - **2025 GST Rationalization Case:** Auto-parts under HSN `8708` were 28% prior to 2025-01-01, and 18% from 2025-01-01 onwards.
   - Invoices dated 2025-01-01 or later charging 28% are flagged for rate overcharge.

4. **CGST and SGST Parity:**
   - Statutory requirement: $\text{CGST Rate} = \text{SGST Rate}$ and $|\text{CGST Amount} - \text{SGST Amount}| \le \text{Roundoff Tolerance}$.

---

### 2.4 Verdict Determination

- **`MATCHED` (Green):**
  - Zero discrepancies, or only benign `INFO` notices. Total Rupee at Risk $= \text{₹0.00}$.
- **`REVIEW` (Amber):**
  - No `ERROR` severity discrepancies. Contains only `WARNING` level notices (e.g., minor quantity variance within receiving norms, missing non-critical header fields).
- **`MISMATCH` (Red):**
  - One or more `ERROR` severity discrepancies (price excess, unreceived goods, wrong GST type, arithmetic failure, invalid GSTIN).
  - Total Rupee at Risk $> \text{₹0.00}$.
