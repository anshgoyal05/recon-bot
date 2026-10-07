# Recon-Bot: System Architecture & Design Specification

Recon-Bot is an enterprise three-way matching platform engineered specifically for Indian manufacturing MSMEs (Micro, Small, and Medium Enterprises). It automates the verification of **Purchase Orders (PO)**, **Supplier Tax Invoices**, and **Goods Receipt Notes (GRN)**.

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion Layer"]
        A[Folder / ZIP / Multi-PDF Drop] --> B[PyMuPDF 200 DPI Renderer]
        B --> C[File Hash SHA-256 Deduplication]
    end

    subgraph AI["2. Vision AI Extraction Layer"]
        C --> D{LLMProvider}
        D -->|Production| E[Gemini Flash 1.5 Vision]
        D -->|Offline Demo| F[MockProvider / Local Fixtures]
        E --> G[Pydantic v2 Schema Validator]
        F --> G
        G -->|Validation Failure| H[Self-Repair Prompt Retry]
        H --> G
    end

    subgraph Grouping["3. Match Set Formation"]
        G --> I[Match Set Grouping Pipeline]
        I -->|1. PO Ref Matching| J[Direct 3-Way Match]
        I -->|2. GSTIN Proximity| K[Vendor Grouping]
        I -->|3. RapidFuzz Line Similarity| L[Fuzzy Set Grouping]
    end

    subgraph Engine["4. Deterministic Reconciliation Engine"]
        J & K & L --> M[Line Item Matcher RapidFuzz]
        M --> N[Quantity Rules]
        M --> O[Unit Price Rules]
        M --> P[Statutory GST Engine]
        P --> Q[Modulo-36 GSTIN Checksum]
        P --> R[Intra/Inter State Tax Routing]
        P --> S[Dynamic HSN Rate by Date]
        M --> T[Arithmetic & Duplicate Rules]
        N & O & P & T --> U[Verdict & Rupee-at-Risk Calculator]
    end

    subgraph Storage["5. Persistence & Workflows"]
        U --> V[(SQLite / Postgres DB via SQLModel)]
        V --> W[SSE Real-time Progress Stream]
        V --> X[Color-Coded Excel Exporter openpyxl]
        V --> Y[LLM Dispute Email Composer]
        V --> Z[Audit Trail & Review Actions]
    end

    subgraph UI["6. Apple Design System Frontend"]
        W & X & Y & Z --> UI1[Next.js 14 App Router]
        UI1 --> UI2[3-Pane Side-by-Side Document Viewer]
        UI1 --> UI3[Glowing Bounding Box Coordinates]
        UI1 --> UI4[3-Way Line Item Comparison Table]
        UI1 --> UI5[Command Palette ⌘K & iOS Settings]
    end
```

---

## 2. Core Architectural Principles

### 2.1 The AI Extracts, The Code Decides
- **No Hallucinated Verdicts:** Large Language Models are employed solely as perceptual vision parsers to convert unstructured invoice PDFs into structured JSON.
- **Pure Python Rules:** Every commercial decision (Quantity tolerance, Unit Price divergence, CGST/SGST splitting, HSN slab adherence) is computed by deterministic, auditable Python code.

### 2.2 Statutory Indian GST Compliance Engine
Recon-Bot enforces statutory requirements defined in the **Central Goods and Services Tax (CGST) Act, 2017** and **Integrated Goods and Services Tax (IGST) Act, 2017**:

1. **GSTIN Modulo-36 Checksum Validation:**
   - 15-character alphanumeric GSTIN validation using the official alphanumeric weighting algorithm:
   $$\text{Weight} = 1 \text{ (even index)}, 2 \text{ (odd index)}$$
   $$\text{Quotient} = \lfloor (\text{Code} \times \text{Weight}) / 36 \rfloor, \quad \text{Remainder} = (\text{Code} \times \text{Weight}) \pmod{36}$$
2. **Tax Routing Verification (Sections 7 & 8 of the IGST Act):**
   - Intra-State supply (Supplier State Code $=$ Place of Supply) $\implies$ **CGST + SGST** (Mandatory 50/50 split).
   - Inter-State supply (Supplier State Code $\ne$ Place of Supply) $\implies$ **IGST**.
   - Flagging Section 16(2) ITC blocking if an intra-state supplier unlawfully charges IGST.
3. **Dynamic, Versioned HSN Rate Lookup:**
   - India's GST council restructured key slabs in 2025 (e.g. HSN 8708 auto components transitioned from 28% to 18% effective January 1, 2025).
   - Rates are dynamically resolved based on **Document Date**, never hardcoded.

---

## 3. Data Model (SQLModel / Relational)

```mermaid
erDiagram
    BATCH ||--o{ DOCUMENT : contains
    BATCH ||--o{ MATCH_SET : groups_into
    MATCH_SET ||--o{ LINE_ITEM : contains
    MATCH_SET ||--o{ DISCREPANCY : flags
    MATCH_SET ||--o{ AUDIT_LOG : tracks
    DOCUMENT ||--o| EXTRACTED_DOC : yields

    BATCH {
        uuid id PK
        string name
        string status
        int total_files
        float total_at_risk_inr
    }

    DOCUMENT {
        uuid id PK
        uuid batch_id FK
        string filename
        string file_hash
        string doc_type
        int page_count
    }

    MATCH_SET {
        uuid id PK
        uuid batch_id FK
        string set_name
        string supplier_gstin
        string verdict
        float total_at_risk_inr
    }

    DISCREPANCY {
        uuid id PK
        uuid match_set_id FK
        string discrepancy_type
        string severity
        string field_name
        string expected_value
        string actual_value
        float impact_inr
        string status
        json bbox_json
    }

    HSN_RATE {
        uuid id PK
        string hsn_code
        float rate_percent
        date effective_from
        date effective_to
    }
```

---

## 4. Bounding Box & Document Page Rendering Pipeline

1. **PyMuPDF Rendering:** Each PDF page is rasterized at **200 DPI** using `fitz.Matrix(200/72, 200/72)` to balance OCR legibility with low memory footprint.
2. **Normalized Coordinate Space:** Bounding boxes are normalized to a standard $[0, 1000]$ integer grid:
   $$top = \frac{ymin}{1000} \times 100\%, \quad left = \frac{xmin}{1000} \times 100\%$$
3. **Interactive UI Overlay:** The Next.js frontend renders high-resolution page PNGs via `GET /api/documents/{id}/page/{n}.png` and positions SVG highlight overlays directly on discrepant cells.

---

## 5. Security & Privacy Design
- **Local SQLite / Self-Hosted Postgres:** No vendor lock-in; MSME invoices remain within the company's premises or private cloud.
- **Offline Mock Provider:** Full system features run offline using deterministic MSME fixtures for air-gapped defense or demo environments.
- **Immutable Audit Trail:** All override actions (`ACCEPTED`, `DISPUTED`, `RESOLVED`) record user identity, timestamp, previous state, and reason in `AuditLog`.
