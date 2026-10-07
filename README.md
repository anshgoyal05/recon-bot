# Recon-Bot ⚡

> **Automated Three-Way Matching (Purchase Order ↔ Supplier Invoice ↔ Goods Receipt Note) Engineered for Indian Manufacturing MSMEs.**

Recon-Bot reads folders of unstructured PDF invoices, purchase orders, and goods receipt notes using vision AI, groups them into match sets, and executes a deterministic statutory rules engine to pinpoint discrepancies in **Quantity, Unit Price, and Indian GST (CGST/SGST/IGST)** before payments are released.

---

## 🌟 Key Highlights

- **Vision AI with Offline Fallback:** Uses Google Gemini Flash 1.5 Vision with structured Pydantic schema enforcement and self-repair retry. If no API key is provided, seamlessly switches to deterministic `MockProvider` using bundled MSME auto-parts fixtures.
- **The AI Extracts, The Code Decides:** Zero hallucinated verdicts. All commercial, mathematical, and tax rules are executed in pure, deterministic, auditable Python.
- **Indian Statutory GST Intelligence:**
  - Full Modulo-36 GSTIN format and checksum validation.
  - Sections 7 & 8 IGST Act tax routing: ensures intra-state transactions charge CGST + SGST (never IGST) and inter-state transactions charge IGST.
  - Dynamic HSN rate lookup keyed by **Invoice Date** (fully compliant with the 2025 GST rationalization, e.g. HSN 8708 auto-components transitioning from 28% to 18%).
- **Apple.com-Level UI/UX:**
  - SF Pro / Inter typographic hierarchy, frosted glass nav (`backdrop-filter: blur(20px)`), light (`#FBFBFD`) and dark (`#000000`) modes.
  - **Hero 3-Pane Viewer:** Side-by-side PO ↔ Invoice ↔ GRN document viewer with SVG glowing bounding-box highlights overlaid on discrepant cells.
  - **Interactive 3-Way Line Item Comparison Table:** Cell-level red/amber diffs with plain-English tooltips.
  - **1-Click Dispute Email Composer:** Synthesizes discrepancies into polite, itemized notices with 1-click clipboard copy.
  - **Export to Excel:** Generates styled, color-coded `.xlsx` workbooks via `openpyxl`.

---

## 🛠 Tech Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + Framer Motion + GSAP + Radix UI + Lucide Icons.
- **Backend:** Python 3.12 + FastAPI + SQLModel (SQLite for local dev, PostgreSQL-ready) + PyMuPDF (fitz 200 DPI rasterizer) + openpyxl + rapidfuzz.
- **AI Vision:** Google Gemini 1.5 Flash via `LLMProvider` interface + `MockProvider`.
- **Infrastructure:** Docker Compose, Makefile one-command startup.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- (Optional) `GEMINI_API_KEY` (system operates completely offline in Mock Mode if omitted)

### Option 1: One-Command Dev Script
```bash
# Setup environments and install dependencies
make setup

# Run backend (port 8000) and frontend (port 3000) concurrently
make dev
```

### Option 2: Run Separately

**Backend:**
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

### Option 3: Docker Compose
```bash
docker-compose up --build
```

---

## 📂 Bundled Sample Dataset (8 Realistic Auto-Parts Scenarios)

Recon-Bot includes a complete ReportLab-generated sample dataset in `/sample_data/pdfs/` with ground truth:

1. **Clean Baseline Set:** Tata AutoComp Systems (`MATCHED`, ₹0 risk).
2. **Short Quantity Received:** Bharat Forge Ltd — 80 pcs received vs 100 pcs invoiced (`MISMATCH`, ₹18,880.00 at risk).
3. **Price Creep / Variance:** Sundram Fasteners Ltd — ₹145/pc vs ₹120/pc PO price (`MISMATCH`, ₹14,750.00 at risk).
4. **Intra-State IGST Violation:** Precision Toolings Pune — Both supplier and buyer in Maharashtra (27), but supplier incorrectly charged 18% IGST (`MISMATCH`, ₹9,000.00 at risk).
5. **Wrong HSN Slab Rate:** Apex Foundry — Steel castings charged at 12% instead of statutory 18% (`MISMATCH`, ₹5,400.00 at risk).
6. **CGST $\ne$ SGST & Math Error:** Motherson Automotive — Asymmetrical rates and line item calculation error (`MISMATCH`, ₹700.00 at risk).
7. **Duplicate Invoice Submission:** Tata AutoComp Systems — Resubmission of previously cleared invoice (`MISMATCH`, ₹81,420.00 at risk).
8. **Multi-Page Heavy Assembly:** JBM Auto Ltd — 6 line items distributed across a 2-page invoice (`MATCHED`, ₹0 risk).

To load all 8 sets instantly in the web app, click **"Load 8-Set MSME Demo"** on the upload screen or landing page.

---

## 🧪 Testing

Run the full backend test suite:
```bash
make test
# or
PYTHONPATH=apps/api apps/api/.venv/bin/pytest apps/api/tests -v
```

**Test Coverage:**
- `test_gstin.py`: Validates statutory Modulo-36 checksum, state codes, and edge cases.
- `test_hsn.py`: Tests date-versioned HSN slab resolution and 2025 GST rationalization.
- `test_rules.py`: Asserts individual rules for quantity, price, tax routing, and duplicates.
- `test_ground_truth.py`: Asserts 100% detection accuracy against the 8 sample ground-truth sets.
- `test_api.py`: Validates FastAPI routes, demo upload, and masters.

---

## 📁 Repository Structure

```
Recon-Bot/
├── apps/
│   ├── api/                     # FastAPI backend
│   │   ├── app/
│   │   │   ├── ai/              # Vision OCR & LLMProvider (Gemini + Mock)
│   │   │   ├── engine/          # Deterministic rules & matching engine
│   │   │   ├── models/          # SQLModel database schemas
│   │   │   ├── routes/          # FastAPI routers
│   │   │   └── services/        # Ingestion pipeline & DB seed
│   │   └── tests/               # Pytest suite
│   └── web/                     # Next.js 14 frontend
│       ├── src/
│       │   ├── app/             # App Router pages (/ & /app/*)
│       │   ├── components/      # Apple design components, 3-pane viewer
│       │   └── lib/             # API client, types, formatters
├── sample_data/                 # Generated PDF sets & ground_truth.json
├── docs/                        # Architecture & reconciliation rules
├── docker-compose.yml           # Production Docker orchestration
├── Makefile                     # Root development tasks
└── README.md                    # Project documentation
```

---

## 📜 Statutory Compliance

Recon-Bot enforces:
- **Central Goods and Services Tax (CGST) Act, 2017** — Section 16(2) conditions for claiming Input Tax Credit (ITC).
- **Integrated Goods and Services Tax (IGST) Act, 2017** — Section 7 (Inter-State supply) & Section 8 (Intra-State supply).
- **GST Council Rate Revisions** — Dynamic HSN lookup supporting the 2025 rate revisions.

---

## 📄 License
MIT License. Built for Indian MSME manufacturing competitiveness.
