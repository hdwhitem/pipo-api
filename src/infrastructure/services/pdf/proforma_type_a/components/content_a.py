# src/infrastructure/services/pdf/proforma_type_b/components/table_content.py
from io import BytesIO
from typing import List, Dict, Optional
from reportlab.platypus import Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def format_currency(value: float, currency: int) -> str:
    symbol = "$" if currency == 1 else "€"
    return f"{symbol}{value:,.2f}"


def build_table_content_component(
    slabs: List,
    sign_stream: Optional[BytesIO],
    discount: float,
    count20ft: int,
    count40ft: int,
    currency: int,
    label: str,
    boxes: str,
    note: str,
    ocean_freight: float,
    gbank_account,
    hscode: str,
    slab_images: Dict[str, BytesIO]
):
    styles = getSampleStyleSheet()

    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=1)
    bold_style = ParagraphStyle('BoldCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1)
    left_bold = ParagraphStyle('LeftBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2)
    left_cell = ParagraphStyle('LeftCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=0)
    small_cell = ParagraphStyle('SmallCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7, alignment=1)

    elements = []

    # TABLA DE PRODUCTOS / SLABS
    col_widths = [60, 100, 65, 50, 40, 40, 52, 50, 110]
    headers = [
        Paragraph("SIZE IN MM", bold_style), Paragraph("DESIGN NAME", bold_style),
        Paragraph("DESIGN IMAGE", bold_style), Paragraph("FINISH", bold_style),
        Paragraph("NO. PALLETS", bold_style), Paragraph("QTY IN SLABS", bold_style),
        Paragraph("SQUARE METER", bold_style), Paragraph("FOB PRICE", bold_style),
        Paragraph("TOTAL AMOUNT", bold_style)
    ]
    table_data = [headers]

    tot_qty = 0
    tot_area = 0.0
    tot_pallets = 0.0
    tot_subtotal = 0.0

    for item in slabs:
        dimensions = f"{item.width * 1000:.0f}X{item.height * 1000:.0f}X{item.thickness}"
        img_bytes = slab_images.get(item.image)
        img = Image(img_bytes, width=25, height=25) if img_bytes else Paragraph("-", cell_style)

        pallet = 0.0 if item.pallet_slabs == 0 else (20.0 if item.qty == 0 else item.qty / item.pallet_slabs)
        area = max(0.0, item.qty * (item.width * item.height))
        amount = item.price * area

        tot_qty += item.qty
        tot_area += area
        tot_pallets += pallet
        tot_subtotal += amount

        table_data.append([
            Paragraph(dimensions, cell_style), Paragraph(item.name, cell_style),
            img, Paragraph(str(item.finished), cell_style),
            Paragraph(f"{pallet:.2f}", cell_style), Paragraph(str(item.qty), cell_style),
            Paragraph(f"{area:.2f}", cell_style), Paragraph(format_currency(item.price, currency), bold_style),
            Paragraph(format_currency(amount, currency), cell_style)
        ])

    containers = " "
    if count20ft == 0 and count40ft > 0:
        containers = f"{count40ft:02d}X40FT"
    elif count40ft == 0 and count20ft > 0:
        containers = f"{count20ft:02d}X20FT"
    elif count40ft > 0 and count20ft > 0:
        containers = f"{count20ft:02d}X20FT & {count40ft:02d}X40FT"

    text_desc = f"TOTAL ORDER OF {containers}. HS-CODE: {hscode}.\nWATER ABSORPTION ≤ 0.05 % ISO 10545-2 & IS 13630-3"

    table_data.append([
        Paragraph(text_desc, bold_style), "", "", "",
        Paragraph(f"{tot_pallets:.1f}", bold_style), Paragraph(str(tot_qty), bold_style),
        Paragraph(f"{tot_area:.2f}", bold_style), "", Paragraph(format_currency(tot_subtotal, currency), bold_style)
    ])

    if discount > 0 or ocean_freight > 0:
        if discount > 0:
            table_data.append(["", "", "", "", "", "", Paragraph("Discount", left_bold), "", Paragraph(format_currency(discount, currency), bold_style)])
        if ocean_freight > 0:
            table_data.append(["", "", "", "", "", "", Paragraph("Ocean Freight", left_bold), "", Paragraph(format_currency(ocean_freight, currency), bold_style)])
        grand_total = tot_subtotal - discount + ocean_freight
        table_data.append(["", "", "", "", "", "", Paragraph("Grand Total", left_bold), "", Paragraph(format_currency(grand_total, currency), bold_style)])

    slabs_table = Table(table_data, colWidths=col_widths)
    slabs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, len(slabs)+1), (3, len(slabs)+1)),
    ]))
    elements.append(slabs_table)
    elements.append(Spacer(1, 10))

    # BANK DETAILS & REMARKS
    bank_data = [
        [Paragraph("BANK DETAILS", bold_style), "", Paragraph("REMARKS", bold_style), ""],
        [Paragraph("BENEFICIARY NAME", left_bold), Paragraph(gbank_account.beneficiary, left_cell), Paragraph("1. Above price is FOB PRICE.", small_cell), ""],
        [Paragraph("BANK NAME", left_bold), Paragraph(gbank_account.bank_name, left_cell), Paragraph("2. Above PI is based on 27 ton (Approx) loadability per 1 x 40FT or 20FT.", small_cell), ""],
        [Paragraph("CURRENCY ACCOUNT", left_bold), Paragraph("USD DOLLAR ($)" if currency == 1 else "EUR EURO (€)", left_cell), Paragraph("3. We required Stamped and signed Proforma invoice as an order confirmation.", small_cell), ""],
        [Paragraph("BANK ACCOUNT NO.", left_bold), Paragraph(gbank_account.bank_account_no, left_cell), Paragraph("4. Tolerance of 05% +/- in quantity should be acceptable.", small_cell), ""],
        [Paragraph("SWIFT CODE", left_bold), Paragraph(gbank_account.swift_code, left_cell), Paragraph("5. Transshipment and partial shipment should be allowed.", cell_style), ""],
        [Paragraph("INTERMEDIARY BANK", left_bold), Paragraph("NA" if currency == 2 else gbank_account.intermediary_bank, left_cell), Paragraph("6. The rate given in the PI is valid till 10 days for confirmation.", small_cell), ""]
    ]

    bank_table = Table(bank_data, colWidths=[110, 160, 148, 149])
    bank_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)), ('SPAN', (2, 0), (3, 0)),
        ('SPAN', (2, 1), (3, 1)), ('SPAN', (2, 2), (3, 2)),
        ('SPAN', (2, 3), (3, 3)), ('SPAN', (2, 4), (3, 4)),
        ('SPAN', (2, 5), (3, 5)), ('SPAN', (2, 6), (3, 6)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 10))

    # PACKING & STICKER
    pack_data = [
        [Paragraph("PALLET & BOX STICKER", bold_style), Paragraph("BOX DESIGN", bold_style), Paragraph("PACKING NOTE", bold_style)],
        [Paragraph(label.upper(), cell_style), Paragraph(boxes.upper(), cell_style), Paragraph(note.upper(), cell_style)]
    ]
    pack_table = Table(pack_data, colWidths=[189, 189, 189])
    pack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(pack_table)
    elements.append(Spacer(1, 10))

    # DECLARACIÓN Y FIRMA
    sign_img = Image(sign_stream, width=140, height=40) if sign_stream else Paragraph("", cell_style)
    decl_text = "DECLARATION: We declare that this invoice shows the actual price of goods described and all particulars are true and correct."

    sign_data = [
        [Paragraph(decl_text, cell_style), Paragraph("For,", cell_style), sign_img],
        ["", Paragraph(gbank_account.beneficiary, small_cell), ""],
        ["", Paragraph("Authorized", cell_style), ""]
    ]

    sign_table = Table(sign_data, colWidths=[267, 140, 160])
    sign_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 2)),
        ('SPAN', (2, 0), (2, 2)),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(sign_table)

    return elements