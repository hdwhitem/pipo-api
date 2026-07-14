from io import BytesIO
from typing import List, Dict, Optional
from reportlab.platypus import Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage


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
    grey_light1 = colors.HexColor("#D0D0D0")
    grey_light2 = colors.HexColor("#E0E0E0")
    grey_light3 = colors.HexColor("#ECECEC")

    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=1, leading=10)
    bold_style = ParagraphStyle('BoldCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1, leading=10)
    left_bold = ParagraphStyle('LeftBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2, leading=10)
    left_cell = ParagraphStyle('LeftCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=0, leading=10)
    small_cell = ParagraphStyle('SmallCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7, alignment=1, leading=9)
    right_bold = ParagraphStyle('RightBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2, leading=10)

    elements = []

    # ═══════════════════════════════════════════════════════
    # TABLA DE PRODUCTOS / SLABS
    # .NET: 60, 120, 65, Relative, 40, 40, Relative, 40, Relative
    # Approx relative widths: ~52, ~53 → col_widths = [60, 120, 65, 52, 40, 40, 53, 40, 97]
    # ═══════════════════════════════════════════════════════
    col_widths = [60, 125, 60, 60, 40, 40, 53, 40, 89]
    headers = [
        Paragraph("SIZE IN MM", bold_style),
        Paragraph("DESIGN NAME", bold_style),
        Paragraph("DESIGN IMAGE", bold_style),
        Paragraph("FINISH", bold_style),
        Paragraph("NO. PALLETS", bold_style),
        Paragraph("QTY IN SLABS", bold_style),
        Paragraph("SQUARE METER", bold_style),
        Paragraph("FOB PRICE", bold_style),
        Paragraph("TOTAL AMOUNT", bold_style),
    ]
    table_data = [headers]

    tot_qty = 0
    tot_area = 0.0
    tot_pallets = 0.0
    tot_subtotal = 0.0

    for item in slabs:
        dimensions = f"{item.width * 1000:.0f}X{item.height * 1000:.0f}X{item.thickness}"

        img_bytes = slab_images.get(item.image)
        if img_bytes:
            pil_img = PILImage.open(img_bytes)
            pil_img = pil_img.transpose(PILImage.Transpose.ROTATE_90)
            rotated = BytesIO()
            pil_img.save(rotated, format='PNG')
            rotated.seek(0)
            img = Image(rotated, width=56, height=28)
            img.hAlign = 'CENTER'
        else:
            img = Paragraph("-", cell_style)

        pallet = 0.0 if item.pallet_slabs == 0 else (20.0 if item.qty == 0 else item.qty / item.pallet_slabs)
        area = max(0.0, item.qty * (item.width * item.height))
        amount = item.price * area

        tot_qty += item.qty
        tot_area += area
        tot_pallets += pallet
        tot_subtotal += amount

        table_data.append([
            Paragraph(dimensions, cell_style),
            Paragraph(item.name, cell_style),
            img,
            Paragraph(str(item.finished), cell_style),
            Paragraph(f"{pallet:.2f}", cell_style),
            Paragraph(str(item.qty), cell_style),
            Paragraph(f"{area:.2f}", cell_style),
            Paragraph(format_currency(item.price, currency), bold_style),
            Paragraph(format_currency(amount, currency), cell_style),
        ])


    containers = " "
    if count20ft == 0 and count40ft > 0:
        containers = f"{'0' if count40ft < 10 else ''}{count40ft}X40FT"
    elif count40ft == 0 and count20ft > 0:
        containers = f"{'0' if count20ft < 10 else ''}{count20ft}X20FT"
    elif count40ft > 0 and count20ft > 0:
        containers = f"0{count20ft}X20FT & 0{count40ft}X40FT"

    text_desc = (
        f"TOTAL ORDER OF {containers}. HS-CODE: {hscode}. <br/>"
        f"WATER ABSORPTION \u2264 0.05 % ISO 10545-2 & IS 13630-3"
    )

    summary_row_idx = len(slabs) + 1

    if discount > 0 or ocean_freight > 0:
        # .NET: RowSpan(4) + ColumnSpan(4) + Grey.Lighten2 bg
        table_data.append([
            Paragraph(text_desc, bold_style), "", "", "",
            Paragraph(f"{tot_pallets:.1f}", bold_style),
            Paragraph(str(tot_qty), bold_style),
            Paragraph(f"{tot_area:.2f}", bold_style),
            "",
            Paragraph(format_currency(tot_subtotal, currency), bold_style),
        ])
        # Discount
        if discount > 0:
            table_data.append([
                "", "", "", "", "", "",
                Paragraph("Discount", right_bold),
                "",
                Paragraph(format_currency(discount, currency), bold_style),
            ])
        # Ocean Freight
        if ocean_freight > 0:
            table_data.append([
                "", "", "", "", "", "",
                Paragraph("Ocean Freight", right_bold),
                "",
                Paragraph(format_currency(ocean_freight, currency), bold_style),
            ])
        # Grand Total
        grand_total = tot_subtotal - discount + ocean_freight
        table_data.append([
            "", "", "", "", "", "",
            Paragraph("Grand Total", right_bold),
            "",
            Paragraph(format_currency(grand_total, currency), bold_style),
        ])
    else:
        # .NET: ColumnSpan(4) sin RowSpan
        table_data.append([
            Paragraph(text_desc.replace("TOTAL ORDER OF ", ""), bold_style), "", "", "",
            Paragraph(f"{tot_pallets:.1f}", bold_style),
            Paragraph(str(tot_qty), bold_style),
            Paragraph(f"{tot_area:.2f}", bold_style),
            "",
            Paragraph(format_currency(tot_subtotal, currency), bold_style),
        ])

    slabs_table = Table(table_data, colWidths=col_widths)

     # ── Total rows ────────────────────────────────────────────────────────
    n        = len(slabs)
    tr       = n + 1                       # first total row index

    slab_style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), grey_light3),
        ('GRID', (0, 0), (-1, n), 0.5, grey_light1),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('SPAN', (0, summary_row_idx), (3, summary_row_idx)),
    ]


    # .NET: Summary text bg = Grey.Lighten2, Total amount bg = Grey.Lighten2
    slab_style_cmds.append(('BACKGROUND', (0, summary_row_idx), (3, summary_row_idx), grey_light2))
    slab_style_cmds.append(('BACKGROUND', (8, summary_row_idx), (8, summary_row_idx), grey_light2))

    # Discount/OceanFreight rows
    if discount > 0 or ocean_freight > 0:
        # .NET: RowSpan(4) on summary text
        total_extra_rows = (1 if discount > 0 else 0) + (1 if ocean_freight > 0 else 0) + 1  # +1 grand total
        slab_style_cmds.append(('SPAN', (0, summary_row_idx), (3, summary_row_idx + total_extra_rows)))
        slab_style_cmds.append(("BACKGROUND", (0, tr), (3, tr + 2), grey_light3))


        row_offset = summary_row_idx + 1
        if discount > 0:
            # .NET: ColumnSpan(2) for label, right-aligned
            slab_style_cmds.append(('SPAN', (6, row_offset), (7, row_offset)))
            slab_style_cmds.append(('ALIGN', (6, row_offset), (7, row_offset), 'RIGHT'))
            slab_style_cmds.append(('BACKGROUND', (8, row_offset), (8, row_offset), grey_light2))
            row_offset += 1

        if ocean_freight > 0:
            slab_style_cmds.append(('SPAN', (6, row_offset), (7, row_offset)))
            slab_style_cmds.append(('ALIGN', (6, row_offset), (7, row_offset), 'RIGHT'))
            slab_style_cmds.append(('BACKGROUND', (8, row_offset), (8, row_offset), grey_light2))
            row_offset += 1

        # Grand Total
        slab_style_cmds.append(('SPAN', (6, row_offset), (7, row_offset)))
        slab_style_cmds.append(('ALIGN', (6, row_offset), (7, row_offset), 'RIGHT'))
        slab_style_cmds.append(('BACKGROUND', (8, row_offset), (8, row_offset), grey_light2))

    slabs_table.setStyle(TableStyle(slab_style_cmds))
    elements.append(slabs_table)
    elements.append(Spacer(1, 14))  # .NET: PaddingTop(0.5cm) ≈ 14pt

    # ═══════════════════════════════════════════════════════
    # BANK DETAILS & REMARKS
    # .NET: 100, RelativeColumn(~217), 125, 125
    # ═══════════════════════════════════════════════════════
    bank_data = [
        [
            Paragraph("BANK DETAILS", bold_style), "",
            Paragraph("REMARKS", bold_style), ""
        ],
        [
            Paragraph("BENEFICIARY NAME", right_bold),
            Paragraph(gbank_account.beneficiary, left_cell),
            Paragraph("1. Above price is FOB PRICE.", small_cell), ""
        ],
        [
            Paragraph("BANK NAME", right_bold),
            Paragraph(gbank_account.bank_name, left_cell),
            Paragraph("2. Above PI is based on 27 ton (Approx) loadability per 1 x 40FT or 20FT.", small_cell), ""
        ],
        [
            Paragraph("CURRENCY ACCOUNT", right_bold),
            Paragraph("USD DOLLAR ($)" if currency == 1 else "EUR EURO (\u20ac)", left_cell),
            Paragraph("3. We required Stamped and signes Proforma invoice as an order confirmation.", small_cell), ""
        ],
        [
            Paragraph("BANK ACCOUNT NO.", right_bold),
            Paragraph(gbank_account.bank_account_no, left_cell),
            Paragraph("4. Tolerance of 05% +/- in quantity should be acceptable.", small_cell), ""
        ],
        [
            Paragraph("SWIFT CODE", right_bold),
            Paragraph(gbank_account.swift_code, left_cell),
            Paragraph("5. Transshipment and partial shipment should be allowed.", cell_style), ""
        ],
        [
            Paragraph("INTERMEDIARY BANK", right_bold),
            Paragraph("NA" if currency == 2 else gbank_account.intermediary_bank, left_cell),
            Paragraph("6. The rate given in the PI is valid till 10 days for confirmation.", small_cell), ""
        ],
    ]

    bank_table = Table(bank_data, colWidths=[100, 217, 125, 125])
    bank_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)), ('SPAN', (2, 0), (3, 0)),
        ('SPAN', (2, 1), (3, 1)), ('SPAN', (2, 2), (3, 2)),
        ('SPAN', (2, 3), (3, 3)), ('SPAN', (2, 4), (3, 4)),
        ('SPAN', (2, 5), (3, 5)), ('SPAN', (2, 6), (3, 6)),
        # Header bg: Grey.Lighten2
        ('BACKGROUND', (0, 0), (-1, 0), grey_light2),
        ('GRID', (0, 0), (-1, -1), 0.5, grey_light1),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 14))

    # ═══════════════════════════════════════════════════════
    # PACKING & STICKER
    # .NET: 3 × RelativeColumn (iguales)
    # ═══════════════════════════════════════════════════════
    pack_data = [
        [
            Paragraph("PALLET & BOX STICKER", bold_style),
            Paragraph("BOX DESIGN", bold_style),
            Paragraph("PACKING NOTE", bold_style),
        ],
        [
            Paragraph(f" {label.upper()} ", cell_style),
            Paragraph(f" {boxes.upper()} ", cell_style),
            Paragraph(f" {note.upper()} ", cell_style),
        ],
    ]
    pack_table = Table(pack_data, colWidths=[189, 189, 189])
    pack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey_light2),
        ('GRID', (0, 0), (-1, -1), 0.5, grey_light1),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(pack_table)
    elements.append(Spacer(1, 14))

    # ═══════════════════════════════════════════════════════
    # DECLARACIÓN Y FIRMA
    # .NET: RelativeColumn(~267), ConstantColumn(140), ConstantColumn(160)
    # .NET: Declaration SIN borde, "For," CON borde, sign CON borde RowSpan(3)
    # .NET typo: "perticulars" (no "particulars")
    # ═══════════════════════════════════════════════════════
    if sign_stream and sign_stream.getvalue():
        sign_img = Image(BytesIO(sign_stream.getvalue()), width=150, height=30)
    else:
        sign_img = Paragraph("", cell_style)

    decl_text = (
        "DECLARATION: We declare that this invoice shows the actual price of goods "
        "described and all perticulars are true and correct."
    )

    sign_data = [
        [Paragraph(decl_text, cell_style), Paragraph("For,", cell_style), sign_img],
        ["", Paragraph(gbank_account.beneficiary, small_cell), ""],
        ["", Paragraph("Authorized", cell_style), ""],
    ]

    sign_table = Table(sign_data, colWidths=[267, 140, 160])
    sign_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 2)),   # Declaration: RowSpan(3)
        ('SPAN', (2, 0), (2, 2)),   # Signature: RowSpan(3)
        ('GRID', (0, 0), (-1, -1), 0.5, grey_light1),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sign_table)

    return elements