import os
import json
import hashlib
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

SAMPLE_DATA_DIR = Path(__file__).resolve().parent
SETS_DIR = SAMPLE_DATA_DIR / "sets"
FIXTURES_DIR = SAMPLE_DATA_DIR / "fixtures"

SETS_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

def compute_file_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_base_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        textColor=colors.HexColor('#1D1D1F'),
        alignment=1, # Center
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#0071E3'),
        alignment=1,
        spaceAfter=15
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#333333')
    )
    bold_meta = ParagraphStyle(
        'DocMetaBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#111111')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=9.5,
        textColor=colors.HexColor('#222222')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9.5,
        textColor=colors.HexColor('#111111')
    )
    return {
        'title': title_style,
        'sub': subtitle_style,
        'meta': meta_style,
        'bold': bold_meta,
        'cell': cell_style,
        'cell_bold': cell_bold,
    }

def create_po_pdf(
    filename: Path,
    po_no: str,
    date: str,
    supplier_name: str,
    supplier_gstin: str,
    supplier_address: str,
    buyer_name: str,
    buyer_gstin: str,
    buyer_address: str,
    items: list,
    terms: str = "Payment 30 days from GRN inspection.",
):
    doc = SimpleDocTemplate(str(filename), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = get_base_styles()
    story = []

    # Title
    story.append(Paragraph("PURCHASE ORDER", styles['title']))
    story.append(Paragraph(f"PO NO: {po_no} | DATE: {date}", styles['sub']))
    story.append(Spacer(1, 10))

    # Parties Meta Table
    buyer_info = f"<b>ISSUED BY (BUYER):</b><br/>{buyer_name}<br/>{buyer_address}<br/><b>GSTIN:</b> {buyer_gstin}<br/><b>State Code:</b> {buyer_gstin[:2]}"
    supplier_info = f"<b>VENDOR / SUPPLIER:</b><br/>{supplier_name}<br/>{supplier_address}<br/><b>GSTIN:</b> {supplier_gstin}<br/><b>State Code:</b> {supplier_gstin[:2]}"
    
    meta_data = [
        [Paragraph(buyer_info, styles['meta']), Paragraph(supplier_info, styles['meta'])],
        [Paragraph(f"<b>Delivery Terms:</b> Ex-works / Door Delivery<br/><b>Payment Terms:</b> {terms}", styles['meta']),
         Paragraph(f"<b>PO Reference:</b> {po_no}<br/><b>Place of Supply:</b> {buyer_gstin[:2]}", styles['meta'])]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#EEEEEE')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Items Table
    headers = ["S.No", "Item Description", "HSN", "Qty", "UoM", "Unit Rate (INR)", "Taxable Value (INR)"]
    table_data = [[Paragraph(f"<b>{h}</b>", styles['cell_bold']) for h in headers]]
    
    total_taxable = 0.0
    for idx, itm in enumerate(items, 1):
        amt = itm['qty'] * itm['rate']
        total_taxable += amt
        row = [
            Paragraph(str(idx), styles['cell']),
            Paragraph(itm['desc'], styles['cell']),
            Paragraph(itm.get('hsn', '7318'), styles['cell']),
            Paragraph(f"{itm['qty']:,.2f}", styles['cell']),
            Paragraph(itm.get('uom', 'PCS'), styles['cell']),
            Paragraph(f"{itm['rate']:,.2f}", styles['cell']),
            Paragraph(f"{amt:,.2f}", styles['cell']),
        ]
        table_data.append(row)

    # Total Row
    table_data.append([
        Paragraph("<b>Total Taxable Value:</b>", styles['cell_bold']), "", "", "", "", "",
        Paragraph(f"<b>INR {total_taxable:,.2f}</b>", styles['cell_bold'])
    ])

    items_table = Table(table_data, colWidths=[30, 190, 50, 55, 45, 80, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E5E5')),
        ('SPAN', (0,-1), (5,-1)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))

    # Signatory
    sig_data = [
        [Paragraph("<b>Standard Terms:</b><br/>1. Goods subject to store inspection at buyer facility.<br/>2. Mention PO Number on all invoices and delivery challans.", styles['meta']),
         Paragraph("<b>For Precision Auto Components Pvt Ltd</b><br/><br/><br/><b>Authorized Signatory</b>", styles['bold'])]
    ]
    sig_table = Table(sig_data, colWidths=[340, 200])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(sig_table)

    doc.build(story)

def create_invoice_pdf(
    filename: Path,
    inv_no: str,
    date: str,
    po_ref: str,
    supplier_name: str,
    supplier_gstin: str,
    supplier_address: str,
    buyer_name: str,
    buyer_gstin: str,
    buyer_address: str,
    items: list, # each has desc, hsn, qty, uom, rate, cgst_r, sgst_r, igst_r, override_taxable, override_cgst_amt, override_sgst_amt
    place_of_supply: str,
    multipage: bool = False,
):
    doc = SimpleDocTemplate(str(filename), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = get_base_styles()
    story = []

    def make_invoice_header():
        elements = []
        elements.append(Paragraph("TAX INVOICE", styles['title']))
        elements.append(Paragraph(f"INVOICE NO: {inv_no} | DATE: {date} | PO REF: {po_ref}", styles['sub']))
        elements.append(Spacer(1, 10))

        sup_info = f"<b>SUPPLIER (CONSIGNOR):</b><br/>{supplier_name}<br/>{supplier_address}<br/><b>GSTIN:</b> {supplier_gstin}<br/><b>State:</b> {supplier_gstin[:2]}"
        buy_info = f"<b>BILLED TO (CONSIGNEE):</b><br/>{buyer_name}<br/>{buyer_address}<br/><b>GSTIN:</b> {buyer_gstin}<br/><b>State:</b> {buyer_gstin[:2]}"
        
        meta_data = [
            [Paragraph(sup_info, styles['meta']), Paragraph(buy_info, styles['meta'])],
            [Paragraph(f"<b>Invoice No:</b> {inv_no}<br/><b>Invoice Date:</b> {date}", styles['meta']),
             Paragraph(f"<b>PO Reference:</b> {po_ref}<br/><b>Place of Supply:</b> {place_of_supply}", styles['meta'])]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#EEEEEE')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))
        return elements

    story.extend(make_invoice_header())

    headers = ["S.No", "Description", "HSN", "Qty", "Rate", "Taxable (INR)", "CGST", "SGST", "IGST", "Line Total"]
    table_data = [[Paragraph(f"<b>{h}</b>", styles['cell_bold']) for h in headers]]

    total_taxable = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0

    for idx, itm in enumerate(items, 1):
        qty = itm['qty']
        rate = itm['rate']
        taxable = itm.get('taxable_value', qty * rate)
        total_taxable += taxable

        cgst_r = itm.get('cgst_r', 0.0)
        sgst_r = itm.get('sgst_r', 0.0)
        igst_r = itm.get('igst_r', 0.0)

        cgst_amt = itm.get('cgst_amt', round(taxable * (cgst_r / 100.0), 2))
        sgst_amt = itm.get('sgst_amt', round(taxable * (sgst_r / 100.0), 2))
        igst_amt = itm.get('igst_amt', round(taxable * (igst_r / 100.0), 2))

        total_cgst += cgst_amt
        total_sgst += sgst_amt
        total_igst += igst_amt

        line_tot = taxable + cgst_amt + sgst_amt + igst_amt

        row = [
            Paragraph(str(idx), styles['cell']),
            Paragraph(itm['desc'], styles['cell']),
            Paragraph(itm.get('hsn', '7318'), styles['cell']),
            Paragraph(f"{qty:,.1f}", styles['cell']),
            Paragraph(f"{rate:,.2f}", styles['cell']),
            Paragraph(f"{taxable:,.2f}", styles['cell']),
            Paragraph(f"{cgst_r}%<br/>{cgst_amt:,.2f}" if cgst_r else "-", styles['cell']),
            Paragraph(f"{sgst_r}%<br/>{sgst_amt:,.2f}" if sgst_r else "-", styles['cell']),
            Paragraph(f"{igst_r}%<br/>{igst_amt:,.2f}" if igst_r else "-", styles['cell']),
            Paragraph(f"{line_tot:,.2f}", styles['cell_bold']),
        ]
        table_data.append(row)

        if multipage and idx == 4:
            # Insert page break for multipage demo
            table_first = Table(table_data, colWidths=[24, 120, 36, 40, 48, 62, 52, 52, 52, 54])
            table_first.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F7')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E5E5')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(table_first)
            story.append(PageBreak())
            story.extend(make_invoice_header())
            table_data = [[Paragraph(f"<b>{h}</b>", styles['cell_bold']) for h in headers]]

    grand_total = total_taxable + total_cgst + total_sgst + total_igst

    # Add Summary Rows
    summary_data = [
        ["Total Taxable Amount:", f"INR {total_taxable:,.2f}"],
        ["Total CGST Amount:", f"INR {total_cgst:,.2f}"],
        ["Total SGST Amount:", f"INR {total_sgst:,.2f}"],
        ["Total IGST Amount:", f"INR {total_igst:,.2f}"],
        ["Grand Total (INR):", f"INR {grand_total:,.2f}"],
    ]

    items_table = Table(table_data, colWidths=[24, 120, 36, 40, 48, 62, 52, 52, 52, 54])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E5E5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Summary and Bank Table
    summary_table_rows = []
    for s_label, s_val in summary_data:
        summary_table_rows.append([
            Paragraph(f"<b>{s_label}</b>", styles['meta']),
            Paragraph(f"<b>{s_val}</b>", styles['bold'])
        ])
    sum_t = Table(summary_table_rows, colWidths=[150, 120])
    sum_t.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, colors.HexColor('#0071E3')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))

    bank_info = (
        "<b>Bank Details for RTGS/NEFT:</b><br/>"
        "Bank: HDFC Bank Ltd, Industrial Estate Branch<br/>"
        "A/C No: 50200012345678 | IFSC: HDFC0000123<br/>"
        "E-Way Bill No: 231456789012"
    )
    bank_p = Paragraph(bank_info, styles['meta'])

    footer_table = Table([[bank_p, sum_t]], colWidths=[270, 270])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E5E5E5')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(footer_table)
    story.append(Spacer(1, 15))

    sig_p = Paragraph(f"<b>For {supplier_name}</b><br/><br/><br/><b>Authorized Signatory</b>", styles['bold'])
    auth_table = Table([[Paragraph("Certified that the particulars given above are true and correct.", styles['meta']), sig_p]], colWidths=[340, 200])
    auth_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(auth_table)

    doc.build(story)

def create_grn_pdf(
    filename: Path,
    grn_no: str,
    date: str,
    po_ref: str,
    invoice_ref: str,
    supplier_name: str,
    supplier_gstin: str,
    vehicle_no: str,
    items: list, # each has desc, hsn, ordered_qty, received_qty, accepted_qty, rejected_qty, remarks
):
    doc = SimpleDocTemplate(str(filename), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = get_base_styles()
    story = []

    story.append(Paragraph("GOODS RECEIPT NOTE (GRN)", styles['title']))
    story.append(Paragraph(f"GRN NO: {grn_no} | DATE: {date} | PO REF: {po_ref}", styles['sub']))
    story.append(Spacer(1, 10))

    meta_info_l = (
        f"<b>SUPPLIER:</b> {supplier_name}<br/>"
        f"<b>SUPPLIER GSTIN:</b> {supplier_gstin}<br/>"
        f"<b>INVOICE REF:</b> {invoice_ref}<br/>"
        f"<b>VEHICLE NO:</b> {vehicle_no}"
    )
    meta_info_r = (
        f"<b>RECEIVING STORE:</b> Central Raw Materials Store<br/>"
        f"<b>PO REF:</b> {po_ref}<br/>"
        f"<b>DATE OF RECEIPT:</b> {date}<br/>"
        f"<b>INSPECTION STATUS:</b> Completed"
    )

    meta_table = Table([[Paragraph(meta_info_l, styles['meta']), Paragraph(meta_info_r, styles['meta'])]], colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    headers = ["S.No", "Description", "HSN", "Ordered Qty", "Received Qty", "Accepted Qty", "Rejected Qty", "Remarks"]
    table_data = [[Paragraph(f"<b>{h}</b>", styles['cell_bold']) for h in headers]]

    for idx, itm in enumerate(items, 1):
        ord_q = itm.get('ordered_qty', itm['received_qty'])
        rec_q = itm['received_qty']
        acc_q = itm.get('accepted_qty', rec_q)
        rej_q = itm.get('rejected_qty', 0.0)
        rem = itm.get('remarks', 'Good condition / Ok')

        row = [
            Paragraph(str(idx), styles['cell']),
            Paragraph(itm['desc'], styles['cell']),
            Paragraph(itm.get('hsn', '7318'), styles['cell']),
            Paragraph(f"{ord_q:,.1f}", styles['cell']),
            Paragraph(f"{rec_q:,.1f}", styles['cell']),
            Paragraph(f"{acc_q:,.1f}", styles['cell_bold']),
            Paragraph(f"{rej_q:,.1f}", styles['cell']),
            Paragraph(rem, styles['cell']),
        ]
        table_data.append(row)

    grn_table = Table(table_data, colWidths=[26, 170, 44, 60, 60, 60, 50, 70])
    grn_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E5E5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(grn_table)
    story.append(Spacer(1, 20))

    sig_data = [
        [Paragraph("<b>Received By:</b><br/>Store Officer: Mahesh Patil<br/>Badge: ST-104", styles['meta']),
         Paragraph("<b>Inspected & Verified By:</b><br/>QC Inspector: Sunil Shinde<br/>Badge: QC-082", styles['meta']),
         Paragraph("<b>Store In-Charge:</b><br/><br/><b>Signature & Stamp</b>", styles['bold'])]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E5E5E5')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sig_table)

    doc.build(story)

def generate_all_samples():
    buyer_name = "Precision Auto Components Pvt Ltd"
    buyer_gstin = "27AAACP1234M1ZG"
    buyer_address = "Plot 42, MIDC Bhosari, Pune - 411026, Maharashtra"

    match_sets = []
    fixtures = {}

    # =========================================================================
    # SET 1: Clean Set (Tata AutoComp Parts) - MATCHED, ₹0 Risk
    # =========================================================================
    set1_dir = SETS_DIR / "set_01_clean"
    set1_dir.mkdir(parents=True, exist_ok=True)
    
    po1_path = set1_dir / "PO_2025_001.pdf"
    inv1_path = set1_dir / "INV_TAC_101.pdf"
    grn1_path = set1_dir / "GRN_2025_001.pdf"

    sup1_name = "Tata AutoComp Systems Ltd"
    sup1_gstin = "27AAACT1234F1ZR"
    sup1_addr = "Survey 284, Maan, Hinjawadi Phase 2, Pune - 411057"

    items1 = [
        {"desc": "High Tensile Flange Bolt M10x50", "hsn": "7318", "qty": 100.0, "rate": 450.0, "uom": "PCS"},
        {"desc": "Hardened Hex Nut M10 Grade 8", "hsn": "7318", "qty": 200.0, "rate": 120.0, "uom": "PCS"}
    ]

    create_po_pdf(po1_path, "PO-2025-001", "2025-02-10", sup1_name, sup1_gstin, sup1_addr, buyer_name, buyer_gstin, buyer_address, items1)
    
    inv_items1 = [
        {"desc": "High Tensile Flange Bolt M10x50", "hsn": "7318", "qty": 100.0, "rate": 450.0, "cgst_r": 9.0, "sgst_r": 9.0, "igst_r": 0.0},
        {"desc": "Hardened Hex Nut M10 Grade 8", "hsn": "7318", "qty": 200.0, "rate": 120.0, "cgst_r": 9.0, "sgst_r": 9.0, "igst_r": 0.0}
    ]
    create_invoice_pdf(inv1_path, "INV-TAC-101", "2025-02-14", "PO-2025-001", sup1_name, sup1_gstin, sup1_addr, buyer_name, buyer_gstin, buyer_address, inv_items1, place_of_supply="27")

    grn_items1 = [
        {"desc": "High Tensile Flange Bolt M10x50", "hsn": "7318", "ordered_qty": 100.0, "received_qty": 100.0, "accepted_qty": 100.0},
        {"desc": "Hardened Hex Nut M10 Grade 8", "hsn": "7318", "ordered_qty": 200.0, "received_qty": 200.0, "accepted_qty": 200.0}
    ]
    create_grn_pdf(grn1_path, "GRN-2025-001", "2025-02-15", "PO-2025-001", "INV-TAC-101", sup1_name, sup1_gstin, "MH-12-RN-4820", grn_items1)

    match_sets.append({
        "id": "set_01",
        "set_name": "Set 01: Clean Auto Fasteners",
        "supplier_name": sup1_name,
        "supplier_gstin": sup1_gstin,
        "po_file": "set_01_clean/PO_2025_001.pdf",
        "invoice_file": "set_01_clean/INV_TAC_101.pdf",
        "grn_file": "set_01_clean/GRN_2025_001.pdf",
        "po_number": "PO-2025-001",
        "invoice_number": "INV-TAC-101",
        "grn_number": "GRN-2025-001",
        "expected_verdict": "MATCHED",
        "expected_total_at_risk_inr": 0.0,
        "expected_discrepancies": []
    })

    # =========================================================================
    # SET 2: Short Supply - Invoiced 100 pcs, Received 80 pcs (₹18,880 at risk)
    # =========================================================================
    set2_dir = SETS_DIR / "set_02_short_qty"
    set2_dir.mkdir(parents=True, exist_ok=True)
    
    po2_path = set2_dir / "PO_2025_002.pdf"
    inv2_path = set2_dir / "INV_BF_202.pdf"
    grn2_path = set2_dir / "GRN_2025_002.pdf"

    sup2_name = "Bharat Forge Ltd"
    sup2_gstin = "27AAACB1234A1ZJ"
    sup2_addr = "Mundhwa Industrial Area, Pune - 411036, Maharashtra"

    items2 = [
        {"desc": "Forged Connecting Rod Forging C70", "hsn": "7326", "qty": 100.0, "rate": 800.0, "uom": "PCS"}
    ]
    create_po_pdf(po2_path, "PO-2025-002", "2025-02-11", sup2_name, sup2_gstin, sup2_addr, buyer_name, buyer_gstin, buyer_address, items2)

    inv_items2 = [
        {"desc": "Forged Connecting Rod Forging C70", "hsn": "7326", "qty": 100.0, "rate": 800.0, "cgst_r": 9.0, "sgst_r": 9.0, "igst_r": 0.0}
    ]
    create_invoice_pdf(inv2_path, "INV-BF-202", "2025-02-15", "PO-2025-002", sup2_name, sup2_gstin, sup2_addr, buyer_name, buyer_gstin, buyer_address, inv_items2, place_of_supply="27")

    grn_items2 = [
        {"desc": "Forged Connecting Rod Forging C70", "hsn": "7326", "ordered_qty": 100.0, "received_qty": 80.0, "accepted_qty": 80.0, "remarks": "Short received 20 pcs at security gate"}
    ]
    create_grn_pdf(grn2_path, "GRN-2025-002", "2025-02-16", "PO-2025-002", "INV-BF-202", sup2_name, sup2_gstin, "MH-14-DT-9912", grn_items2)

    match_sets.append({
        "id": "set_02",
        "set_name": "Set 02: Short Quantity Received",
        "supplier_name": sup2_name,
        "supplier_gstin": sup2_gstin,
        "po_file": "set_02_short_qty/PO_2025_002.pdf",
        "invoice_file": "set_02_short_qty/INV_BF_202.pdf",
        "grn_file": "set_02_short_qty/GRN_2025_002.pdf",
        "po_number": "PO-2025-002",
        "invoice_number": "INV-BF-202",
        "grn_number": "GRN-2025-002",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 18880.0,
        "expected_discrepancies": [
            {
                "type": "QUANTITY",
                "severity": "ERROR",
                "field": "quantity",
                "expected": "80.0",
                "actual": "100.0",
                "impact_inr": 18880.0,
                "explanation": "Invoiced quantity (100.0 PCS) exceeds physically received & accepted quantity on GRN (80.0 PCS) by 20.0 PCS."
            }
        ]
    })

    # =========================================================================
    # SET 3: Unit Price Creep - PO ₹120 vs Invoice ₹145 for 500 pcs (₹14,750 Risk)
    # =========================================================================
    set3_dir = SETS_DIR / "set_03_price_creep"
    set3_dir.mkdir(parents=True, exist_ok=True)
    
    po3_path = set3_dir / "PO_2025_003.pdf"
    inv3_path = set3_dir / "INV_SF_303.pdf"
    grn3_path = set3_dir / "GRN_2025_003.pdf"

    sup3_name = "Sundram Fasteners Ltd"
    sup3_gstin = "33AAACS1234D1Z3"
    sup3_addr = "Padi, Chennai - 600050, Tamil Nadu"

    items3 = [
        {"desc": "Hardened Stud M12x75 High Strength", "hsn": "7318", "qty": 500.0, "rate": 120.0, "uom": "PCS"}
    ]
    create_po_pdf(po3_path, "PO-2025-003", "2025-02-12", sup3_name, sup3_gstin, sup3_addr, buyer_name, buyer_gstin, buyer_address, items3)

    inv_items3 = [
        {"desc": "Hardened Stud M12x75 High Strength", "hsn": "7318", "qty": 500.0, "rate": 145.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0}
    ]
    create_invoice_pdf(inv3_path, "INV-SF-303", "2025-02-16", "PO-2025-003", sup3_name, sup3_gstin, sup3_addr, buyer_name, buyer_gstin, buyer_address, inv_items3, place_of_supply="27")

    grn_items3 = [
        {"desc": "Hardened Stud M12x75 High Strength", "hsn": "7318", "ordered_qty": 500.0, "received_qty": 500.0, "accepted_qty": 500.0}
    ]
    create_grn_pdf(grn3_path, "GRN-2025-003", "2025-02-18", "PO-2025-003", "INV-SF-303", sup3_name, sup3_gstin, "TN-09-CB-1234", grn_items3)

    match_sets.append({
        "id": "set_03",
        "set_name": "Set 03: Unit Price Variance",
        "supplier_name": sup3_name,
        "supplier_gstin": sup3_gstin,
        "po_file": "set_03_price_creep/PO_2025_003.pdf",
        "invoice_file": "set_03_price_creep/INV_SF_303.pdf",
        "grn_file": "set_03_price_creep/GRN_2025_003.pdf",
        "po_number": "PO-2025-003",
        "invoice_number": "INV-SF-303",
        "grn_number": "GRN-2025-003",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 14750.0,
        "expected_discrepancies": [
            {
                "type": "UNIT_PRICE",
                "severity": "ERROR",
                "field": "unit_price",
                "expected": "120.00",
                "actual": "145.00",
                "impact_inr": 14750.0,
                "explanation": "Billed unit price (₹145.00) exceeds agreed PO unit price (₹120.00) by ₹25.00 (+20.8%)."
            }
        ]
    })

    # =========================================================================
    # SET 4: Tax Type Mismatch (Intra-state billed as IGST) - ₹9,000 Risk
    # =========================================================================
    set4_dir = SETS_DIR / "set_04_tax_type"
    set4_dir.mkdir(parents=True, exist_ok=True)
    
    po4_path = set4_dir / "PO_2025_004.pdf"
    inv4_path = set4_dir / "INV_MH_404.pdf"
    grn4_path = set4_dir / "GRN_2025_004.pdf"

    sup4_name = "Precision Toolings Pune"
    sup4_gstin = "27AABCP5678Q1ZJ"
    sup4_addr = "Plot 18, Chakan Industrial Phase 2, Pune - 410501"

    items4 = [
        {"desc": "Precision Stamping Die Plate D2", "hsn": "7326", "qty": 1.0, "rate": 50000.0, "uom": "SET"}
    ]
    create_po_pdf(po4_path, "PO-2025-004", "2025-02-14", sup4_name, sup4_gstin, sup4_addr, buyer_name, buyer_gstin, buyer_address, items4)

    # Invoiced intra-state (27 to 27) with IGST 18% instead of CGST 9% + SGST 9%!
    inv_items4 = [
        {"desc": "Precision Stamping Die Plate D2", "hsn": "7326", "qty": 1.0, "rate": 50000.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0}
    ]
    create_invoice_pdf(inv4_path, "INV-MH-404", "2025-02-18", "PO-2025-004", sup4_name, sup4_gstin, sup4_addr, buyer_name, buyer_gstin, buyer_address, inv_items4, place_of_supply="27")

    grn_items4 = [
        {"desc": "Precision Stamping Die Plate D2", "hsn": "7326", "ordered_qty": 1.0, "received_qty": 1.0, "accepted_qty": 1.0}
    ]
    create_grn_pdf(grn4_path, "GRN-2025-004", "2025-02-19", "PO-2025-004", "INV-MH-404", sup4_name, sup4_gstin, "MH-12-PQ-5544", grn_items4)

    match_sets.append({
        "id": "set_04",
        "set_name": "Set 04: Intra-State IGST Violation",
        "supplier_name": sup4_name,
        "supplier_gstin": sup4_gstin,
        "po_file": "set_04_tax_type/PO_2025_004.pdf",
        "invoice_file": "set_04_tax_type/INV_MH_404.pdf",
        "grn_file": "set_04_tax_type/GRN_2025_004.pdf",
        "po_number": "PO-2025-004",
        "invoice_number": "INV-MH-404",
        "grn_number": "GRN-2025-004",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 9000.0,
        "expected_discrepancies": [
            {
                "type": "TAX_GST",
                "severity": "ERROR",
                "field": "tax_type",
                "expected": "CGST (9.0%) + SGST (9.0%)",
                "actual": "IGST (18.0%)",
                "impact_inr": 9000.0,
                "explanation": "Intra-state supply (Supplier State 27 ↔ Place of Supply 27) incorrectly charged IGST. Under Section 7/8 IGST Act, CGST + SGST is legally mandated."
            }
        ]
    })

    # =========================================================================
    # SET 5: Wrong HSN Rate - HSN 7325 Castings statutory rate is 18%, billed at 12%
    # =========================================================================
    set5_dir = SETS_DIR / "set_05_wrong_hsn_rate"
    set5_dir.mkdir(parents=True, exist_ok=True)
    
    po5_path = set5_dir / "PO_2025_005.pdf"
    inv5_path = set5_dir / "INV_CF_505.pdf"
    grn5_path = set5_dir / "GRN_2025_005.pdf"

    sup5_name = "Apex Foundry & Castings Pvt Ltd"
    sup5_gstin = "27AAACA9999M1ZR"
    sup5_addr = "Plot 5, Kolhapur Foundry Cluster, Kolhapur - 416122"

    items5 = [
        {"desc": "Machined Cast Iron Bearing Housing", "hsn": "7325", "qty": 150.0, "rate": 600.0, "uom": "PCS"}
    ]
    create_po_pdf(po5_path, "PO-2025-005", "2025-02-15", sup5_name, sup5_gstin, sup5_addr, buyer_name, buyer_gstin, buyer_address, items5)

    # Invoiced at 12% total (6% + 6%) instead of statutory 18% (9% + 9%)
    inv_items5 = [
        {"desc": "Machined Cast Iron Bearing Housing", "hsn": "7325", "qty": 150.0, "rate": 600.0, "cgst_r": 6.0, "sgst_r": 6.0, "igst_r": 0.0}
    ]
    create_invoice_pdf(inv5_path, "INV-CF-505", "2025-02-20", "PO-2025-005", sup5_name, sup5_gstin, sup5_addr, buyer_name, buyer_gstin, buyer_address, inv_items5, place_of_supply="27")

    grn_items5 = [
        {"desc": "Machined Cast Iron Bearing Housing", "hsn": "7325", "ordered_qty": 150.0, "received_qty": 150.0, "accepted_qty": 150.0}
    ]
    create_grn_pdf(grn5_path, "GRN-2025-005", "2025-02-22", "PO-2025-005", "INV-CF-505", sup5_name, sup5_gstin, "MH-09-AL-4100", grn_items5)

    match_sets.append({
        "id": "set_05",
        "set_name": "Set 05: Incorrect HSN GST Slab",
        "supplier_name": sup5_name,
        "supplier_gstin": sup5_gstin,
        "po_file": "set_05_wrong_hsn_rate/PO_2025_005.pdf",
        "invoice_file": "set_05_wrong_hsn_rate/INV_CF_505.pdf",
        "grn_file": "set_05_wrong_hsn_rate/GRN_2025_005.pdf",
        "po_number": "PO-2025-005",
        "invoice_number": "INV-CF-505",
        "grn_number": "GRN-2025-005",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 5400.0,
        "expected_discrepancies": [
            {
                "type": "TAX_GST",
                "severity": "ERROR",
                "field": "hsn_rate",
                "expected": "18.0%",
                "actual": "12.0%",
                "impact_inr": 5400.0,
                "explanation": "GST rate for HSN 7325 (Cast articles of iron/steel) is 18.0% as per statutory HSN rate master for date 2025-02-20, but invoice charged 12.0%."
            }
        ]
    })

    # =========================================================================
    # SET 6: CGST ≠ SGST & Line Item Math Mismatch
    # =========================================================================
    set6_dir = SETS_DIR / "set_06_cgst_sgst_mismatch"
    set6_dir.mkdir(parents=True, exist_ok=True)
    
    po6_path = set6_dir / "PO_2025_006.pdf"
    inv6_path = set6_dir / "INV_MA_606.pdf"
    grn6_path = set6_dir / "GRN_2025_006.pdf"

    sup6_name = "Motherson Automotive Technologies"
    sup6_gstin = "27AAACM1234E1Z0"
    sup6_addr = "Gat 412, Mahalunge, Chakan, Pune - 410501"

    items6 = [
        {"desc": "Engine Valve Guide Spec 4", "hsn": "8481", "qty": 100.0, "rate": 500.0, "uom": "PCS"}
    ]
    create_po_pdf(po6_path, "PO-2025-006", "2025-02-16", sup6_name, sup6_gstin, sup6_addr, buyer_name, buyer_gstin, buyer_address, items6)

    # Taxable: 50,000. CGST @ 9% = 4,500. But SGST wrongly injected as 5,200!
    inv_items6 = [
        {
            "desc": "Engine Valve Guide Spec 4",
            "hsn": "8481",
            "qty": 100.0,
            "rate": 500.0,
            "taxable_value": 50000.0,
            "cgst_r": 9.0,
            "cgst_amt": 4500.0,
            "sgst_r": 9.0,
            "sgst_amt": 5200.0, # Mismatch!
            "igst_r": 0.0
        }
    ]
    create_invoice_pdf(inv6_path, "INV-MA-606", "2025-02-21", "PO-2025-006", sup6_name, sup6_gstin, sup6_addr, buyer_name, buyer_gstin, buyer_address, inv_items6, place_of_supply="27")

    grn_items6 = [
        {"desc": "Engine Valve Guide Spec 4", "hsn": "8481", "ordered_qty": 100.0, "received_qty": 100.0, "accepted_qty": 100.0}
    ]
    create_grn_pdf(grn6_path, "GRN-2025-006", "2025-02-22", "PO-2025-006", "INV-MA-606", sup6_name, sup6_gstin, "MH-12-MN-7788", grn_items6)

    match_sets.append({
        "id": "set_06",
        "set_name": "Set 06: CGST ≠ SGST Asymmetry",
        "supplier_name": sup6_name,
        "supplier_gstin": sup6_gstin,
        "po_file": "set_06_cgst_sgst_mismatch/PO_2025_006.pdf",
        "invoice_file": "set_06_cgst_sgst_mismatch/INV_MA_606.pdf",
        "grn_file": "set_06_cgst_sgst_mismatch/GRN_2025_006.pdf",
        "po_number": "PO-2025-006",
        "invoice_number": "INV-MA-606",
        "grn_number": "GRN-2025-006",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 700.0,
        "expected_discrepancies": [
            {
                "type": "TAX_GST",
                "severity": "ERROR",
                "field": "cgst_sgst_equality",
                "expected": "CGST ₹4,500.00 == SGST ₹4,500.00",
                "actual": "CGST ₹4,500.00 != SGST ₹5,200.00",
                "impact_inr": 700.0,
                "explanation": "Intra-state GST rules mandate that CGST and SGST rates and computed amounts must be strictly identical. Discrepancy of ₹700.00 detected."
            }
        ]
    })

    # =========================================================================
    # SET 7: Duplicate Invoice Detection
    # =========================================================================
    set7_dir = SETS_DIR / "set_07_duplicate"
    set7_dir.mkdir(parents=True, exist_ok=True)
    
    po7_path = set7_dir / "PO_2025_007.pdf"
    inv7_path = set7_dir / "INV_TAC_101_DUP.pdf" # Reusing INV-TAC-101 invoice number!
    grn7_path = set7_dir / "GRN_2025_007.pdf"

    create_po_pdf(po7_path, "PO-2025-007", "2025-02-18", sup1_name, sup1_gstin, sup1_addr, buyer_name, buyer_gstin, buyer_address, items1)
    create_invoice_pdf(inv7_path, "INV-TAC-101", "2025-02-19", "PO-2025-007", sup1_name, sup1_gstin, sup1_addr, buyer_name, buyer_gstin, buyer_address, inv_items1, place_of_supply="27")
    create_grn_pdf(grn7_path, "GRN-2025-007", "2025-02-20", "PO-2025-007", "INV-TAC-101", sup1_name, sup1_gstin, "MH-12-RN-4820", grn_items1)

    match_sets.append({
        "id": "set_07",
        "set_name": "Set 07: Duplicate Invoice Submission",
        "supplier_name": sup1_name,
        "supplier_gstin": sup1_gstin,
        "po_file": "set_07_duplicate/PO_2025_007.pdf",
        "invoice_file": "set_07_duplicate/INV_TAC_101_DUP.pdf",
        "grn_file": "set_07_duplicate/GRN_2025_007.pdf",
        "po_number": "PO-2025-007",
        "invoice_number": "INV-TAC-101",
        "grn_number": "GRN-2025-007",
        "expected_verdict": "MISMATCH",
        "expected_total_at_risk_inr": 81420.0,
        "expected_discrepancies": [
            {
                "type": "DUPLICATE",
                "severity": "ERROR",
                "field": "invoice_number",
                "expected": "Unique Invoice Number",
                "actual": "INV-TAC-101 already exists for supplier Tata AutoComp Systems Ltd",
                "impact_inr": 81420.0,
                "explanation": "Duplicate invoice submission detected: Invoice #INV-TAC-101 was previously billed and processed in Set 01."
            }
        ]
    })

    # =========================================================================
    # SET 8: Multi-Page Engineering Order with Partial Delivery (Warning / Review)
    # =========================================================================
    set8_dir = SETS_DIR / "set_08_multipage"
    set8_dir.mkdir(parents=True, exist_ok=True)
    
    po8_path = set8_dir / "PO_2025_008.pdf"
    inv8_path = set8_dir / "INV_JBM_808.pdf"
    grn8_path = set8_dir / "GRN_2025_008.pdf"

    sup8_name = "JBM Auto Ltd"
    sup8_gstin = "06AAACJ1234G1Z3"
    sup8_addr = "Plot 5, Sector 25, Ballabgarh, Faridabad - 121004, Haryana"

    items8 = [
        {"desc": "Exhaust Manifold Stamping Left", "hsn": "8708", "qty": 50.0, "rate": 1200.0, "uom": "PCS"},
        {"desc": "Exhaust Manifold Stamping Right", "hsn": "8708", "qty": 50.0, "rate": 1200.0, "uom": "PCS"},
        {"desc": "Heat Shield Bracket Bracket Type A", "hsn": "8708", "qty": 100.0, "rate": 350.0, "uom": "PCS"},
        {"desc": "Silencer Mounting Flange 3-Hole", "hsn": "8708", "qty": 80.0, "rate": 450.0, "uom": "PCS"},
        {"desc": "Catalytic Converter Outer Shell 2.0L", "hsn": "8708", "qty": 40.0, "rate": 2500.0, "uom": "PCS"},
        {"desc": "Baffle Plate Assembly Pressing", "hsn": "8708", "qty": 60.0, "rate": 650.0, "uom": "PCS"}
    ]
    create_po_pdf(po8_path, "PO-2025-008", "2025-02-18", sup8_name, sup8_gstin, sup8_addr, buyer_name, buyer_gstin, buyer_address, items8)

    inv_items8 = [
        {"desc": "Exhaust Manifold Stamping Left", "hsn": "8708", "qty": 50.0, "rate": 1200.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0},
        {"desc": "Exhaust Manifold Stamping Right", "hsn": "8708", "qty": 50.0, "rate": 1200.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0},
        {"desc": "Heat Shield Bracket Bracket Type A", "hsn": "8708", "qty": 100.0, "rate": 350.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0},
        {"desc": "Silencer Mounting Flange 3-Hole", "hsn": "8708", "qty": 80.0, "rate": 450.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0},
        {"desc": "Catalytic Converter Outer Shell 2.0L", "hsn": "8708", "qty": 40.0, "rate": 2500.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0},
        {"desc": "Baffle Plate Assembly Pressing", "hsn": "8708", "qty": 60.0, "rate": 650.0, "cgst_r": 0.0, "sgst_r": 0.0, "igst_r": 18.0}
    ]
    create_invoice_pdf(inv8_path, "INV-JBM-808", "2025-02-23", "PO-2025-008", sup8_name, sup8_gstin, sup8_addr, buyer_name, buyer_gstin, buyer_address, inv_items8, place_of_supply="27", multipage=True)

    grn_items8 = [
        {"desc": "Exhaust Manifold Stamping Left", "hsn": "8708", "ordered_qty": 50.0, "received_qty": 50.0, "accepted_qty": 50.0},
        {"desc": "Exhaust Manifold Stamping Right", "hsn": "8708", "ordered_qty": 50.0, "received_qty": 50.0, "accepted_qty": 50.0},
        {"desc": "Heat Shield Bracket Bracket Type A", "hsn": "8708", "ordered_qty": 100.0, "received_qty": 100.0, "accepted_qty": 100.0},
        {"desc": "Silencer Mounting Flange 3-Hole", "hsn": "8708", "ordered_qty": 80.0, "received_qty": 80.0, "accepted_qty": 80.0},
        {"desc": "Catalytic Converter Outer Shell 2.0L", "hsn": "8708", "ordered_qty": 40.0, "received_qty": 40.0, "accepted_qty": 40.0},
        {"desc": "Baffle Plate Assembly Pressing", "hsn": "8708", "ordered_qty": 60.0, "received_qty": 60.0, "accepted_qty": 60.0}
    ]
    create_grn_pdf(grn8_path, "GRN-2025-008", "2025-02-24", "PO-2025-008", "INV-JBM-808", sup8_name, sup8_gstin, "HR-55-AA-1002", grn_items8)

    match_sets.append({
        "id": "set_08",
        "set_name": "Set 08: Multi-Page Engineering Assembly",
        "supplier_name": sup8_name,
        "supplier_gstin": sup8_gstin,
        "po_file": "set_08_multipage/PO_2025_008.pdf",
        "invoice_file": "set_08_multipage/INV_JBM_808.pdf",
        "grn_file": "set_08_multipage/GRN_2025_008.pdf",
        "po_number": "PO-2025-008",
        "invoice_number": "INV-JBM-808",
        "grn_number": "GRN-2025-008",
        "expected_verdict": "MATCHED",
        "expected_total_at_risk_inr": 0.0,
        "expected_discrepancies": []
    })

    # Save Ground Truth
    ground_truth = {
        "version": "1.0",
        "company": buyer_name,
        "buyer_gstin": buyer_gstin,
        "sets_count": len(match_sets),
        "sets": match_sets
    }
    with open(SAMPLE_DATA_DIR / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    # Pre-generate JSON fixtures for MockProvider
    # Compute SHA-256 for each PDF and save fixture mapped to both filename and file hash
    print(f"Generated {len(match_sets)} match sets successfully in {SETS_DIR}.")
    print(f"Ground truth written to {SAMPLE_DATA_DIR / 'ground_truth.json'}.")

if __name__ == "__main__":
    generate_all_samples()
