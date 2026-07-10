# src/infrastructure/services/pdf/components/content.py
from io import BytesIO
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image as RLImage

from src.infrastructure.services.pdf.utils.number_to_words import amount_to_words


def _format_currency(value: float, currency_type: int) -> str:
    symbol = "$" if currency_type == 1 else "€"
    return f"{symbol}{value:,.2f}"


def build_content_component(
    order, 
    slab_images: Dict[str, BytesIO], 
    sign_stream: Optional[BytesIO] = None
) -> List:
    elements = []

    # --- 1. ESTILOS DE TEXTO ---
    styles = getSampleStyleSheet()
    
    cell_style = ParagraphStyle('Cell', fontName='Helvetica', fontSize=7, alignment=1, leading=9)
    cell_left_style = ParagraphStyle('CellLeft', fontName='Helvetica', fontSize=7, alignment=0, leading=9)
    cell_right_style = ParagraphStyle('CellRight', fontName='Helvetica', fontSize=7, alignment=2, leading=9)
    
    header_cell_style = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=7, alignment=1, leading=9)
    header_left_style = ParagraphStyle('HCellLeft', fontName='Helvetica-Bold', fontSize=7, alignment=0, leading=9)
    header_right_style = ParagraphStyle('HCellRight', fontName='Helvetica-Bold', fontSize=7, alignment=2, leading=9)
    
    label_u_style = ParagraphStyle('LabelU', fontName='Helvetica-Bold', fontSize=8, leading=10)
    label_u_right_style = ParagraphStyle('LabelURight', fontName='Helvetica-Bold', fontSize=8, alignment=2, leading=10)

    # --- 2. CÁLCULOS SOBRE LOS SLABS / PRODUCTOS ---
    total_qty = 0
    total_area = 0.0
    total_pallets = 0.0
    subtotal = 0.0

    table_data = [[
        Paragraph("SIZE IN MM", header_cell_style),
        Paragraph("DESCRIPTION OF THE ITEM", header_cell_style),
        Paragraph("ITEM IMAGE", header_cell_style),
        Paragraph("FINISHING", header_cell_style),
        Paragraph("NO. PCS", header_cell_style),
        Paragraph("NO. CRATES", header_cell_style),
        Paragraph("SQUARE METER", header_cell_style),
        Paragraph("PRICE USD" if order.currency == 1 else "PRICE EUR", header_cell_style),
        Paragraph("TOTAL AMOUNT", header_cell_style),
    ]]

    for slab in order.slabs:
        # Lógica de Pallets
        current_pallet_slabs_r = slab.pallet_slabs if slab.pallet_slabs else 1
        if current_pallet_slabs_r == 0:
            pallet_r = 0.0
        else:
            pallet_r = 20.0 if slab.qty == 0 else (slab.qty / current_pallet_slabs_r)

        # Lógica de Área
        area_r = slab.qty * (slab.width * slab.height)
        calculated_area = area_r if area_r >= 1 else 0.0

        # Subtotal
        calculated_subtotal = (slab.price or 0.0) * calculated_area

        total_qty += slab.qty
        total_area += calculated_area
        total_pallets += pallet_r
        subtotal += calculated_subtotal

        dims = f"{int(slab.width * 1000)}X{int(slab.height * 1000)}X{slab.thickness}"
        
        # Imagen
        img_stream = slab_images.get(slab.image)
        if img_stream:
            img_element = RLImage(img_stream, width=1 * cm, height=1 * cm)
            img_element.hAlign = 'CENTER'
        else:
            img_element = Paragraph("No Image", ParagraphStyle('NoImg', fontName='Helvetica', fontSize=6, alignment=1))

        table_data.append([
            Paragraph(dims, cell_style),
            Paragraph(slab.name, cell_style),
            img_element,
            Paragraph(slab.finished, cell_style),
            Paragraph(str(slab.qty), cell_style),
            Paragraph(f"{pallet_r:.2f}", cell_style),
            Paragraph(f"{calculated_area:.2f}", cell_style),
            Paragraph(_format_currency(slab.price or 0.0, order.currency), header_cell_style),
            Paragraph(_format_currency(calculated_subtotal, order.currency), cell_style)
        ])

    # --- 3. LÓGICA DE CONTENEDORES Y TOTALES ---
    count_20ft = getattr(order, 'count_20ft', 0)
    count_40ft = getattr(order, 'count_40ft', 0)

    containers = " "
    if count_20ft == 0 and count_40ft > 0:
        containers = f"{count_40ft}X40FT" if count_40ft > 9 else f"0{count_40ft}X40FT"
    elif count_40ft == 0 and count_20ft > 0:
        containers = f"{count_20ft}X20FT" if count_20ft > 9 else f"0{count_20ft}X20FT"
    elif count_40ft > 0 and count_20ft > 0:
        containers = f"0{count_20ft}X20FT & 0{count_40ft}X40FT"

    total_order_text = f"TOTAL ORDER OF {containers}. HS-CODE: {order.hscode_id}."
    grand_total = subtotal - order.discount + order.ocean_freight

    # Fila base de totales
    table_data.append([
        Paragraph(total_order_text, header_cell_style),
        "", "", "", # Celdas unidas por SPAN
        Paragraph(str(total_qty), header_cell_style),
        Paragraph(f"{total_pallets:.1f}", header_cell_style),
        Paragraph(f"{total_area:.2f}", header_cell_style),
        "",
        Paragraph(_format_currency(subtotal, order.currency), header_cell_style)
    ])

    # Filas opcionales (Descuento, Flete Marítimo, Total General)
    has_discount = order.discount > 0
    has_freight = order.ocean_freight > 0

    if has_discount:
        table_data.append([
            "", "", "", "", "", "",
            Paragraph("Discount", header_right_style),
            "",
            Paragraph(_format_currency(order.discount, order.currency), header_cell_style)
        ])

    if has_freight:
        table_data.append([
            "", "", "", "", "", "",
            Paragraph("Ocean Freight", header_right_style),
            "",
            Paragraph(_format_currency(order.ocean_freight, order.currency), header_cell_style)
        ])

    if has_discount or has_freight:
        table_data.append([
            "", "", "", "", "", "",
            Paragraph("Grand Total", header_right_style),
            "",
            Paragraph(_format_currency(grand_total, order.currency), header_cell_style)
        ])

    # Anchos exactos para 19cm (A4 imprimible)
    products_table = Table(table_data, colWidths=[55, 110, 50, 55, 35, 45, 55, 60, 75])
    
    # Estilizado dinámico de la tabla de productos
    base_table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]

    # Calcular Span de la primera fila de totales
    first_total_row_idx = len(order.slabs) + 1
    
    # Determinar Span del total text segun filas extras
    extra_rows = (1 if has_discount else 0) + (1 if has_freight else 0) + (1 if (has_discount or has_freight) else 0)
    
    if extra_rows > 0:
        base_table_style.append(('SPAN', (0, first_total_row_idx), (3, first_total_row_idx + extra_rows)))
        base_table_style.append(('BACKGROUND', (0, first_total_row_idx), (3, first_total_row_idx + extra_rows), colors.HexColor("#E0E0E0")))
    else:
        base_table_style.append(('SPAN', (0, first_total_row_idx), (3, first_total_row_idx)))
        base_table_style.append(('BACKGROUND', (0, first_total_row_idx), (-1, first_total_row_idx), colors.HexColor("#E0E0E0")))

    # Colorear fondo de las filas de totales extras
    if extra_rows > 0:
        for idx in range(first_total_row_idx, first_total_row_idx + extra_rows + 1):
            base_table_style.append(('BACKGROUND', (4, idx), (-1, idx), colors.HexColor("#E0E0E0")))
            base_table_style.append(('SPAN', (6, idx), (7, idx))) # Unir etiqueta "Discount/Freight/Grand Total"

    products_table.setStyle(TableStyle(base_table_style))
    elements.append(products_table)
    elements.append(Spacer(1, 6))

    # --- 4. AMOUNT CHARGEABLE IN WORDS ---
    currency_code = "USD" if order.currency == 1 else "EUR"
    words_text = amount_to_words(grand_total, currency_code).upper()

    words_table = Table([
        [Paragraph("<u><b>AMOUNT CHARGEABLE IN WORDS :</b></u>", ParagraphStyle('WHead', fontName='Helvetica-Bold', fontSize=9, leading=11))],
        [Paragraph(words_text, cell_style)]
    ], colWidths=['100%'])
    words_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('ALIGN', (0, 1), (0, 1), 'CENTER')
    ]))
    elements.append(words_table)
    elements.append(Spacer(1, 6))

    # --- 5. INFORMACIÓN BANCARIA Y EMBALAJE ---
    bank = order.bank
    currency_str = "USD DOLLAR ($)" if order.currency == 1 else "EUR EURO (€)"
    intermediary = "NA" if order.currency == 2 else (getattr(bank, 'intermediary_bank', '') or '')

    bank_table_data = [
        [
            Paragraph("<u><b>OUR BANK DETAILS :</b></u>", ParagraphStyle('BTitle', fontName='Helvetica-Bold', fontSize=9, leading=11)),
            "",
            Paragraph("<u><b>PALLET & BOX STICKER :</b></u>", ParagraphStyle('STitle', fontName='Helvetica-Bold', fontSize=8, leading=10)),
            ""
        ],
        [
            Paragraph("<u><b>BENEFICIARY NAME :</b></u>", label_u_right_style),
            Paragraph(bank.beneficiary, cell_left_style),
            Paragraph(order.box_sticker.upper(), cell_style),
            ""
        ],
        [
            Paragraph("<u><b>BANK NAME :</b></u>", label_u_right_style),
            Paragraph(bank.bank_name, cell_left_style),
            Paragraph("<u><b>BOX DESIGN :</b></u>", label_u_style),
            ""
        ],
        [
            Paragraph("<u><b>CURRENCY ACCOUNT :</b></u>", label_u_right_style),
            Paragraph(currency_str, cell_left_style),
            Paragraph(order.box_design.upper(), cell_style),
            ""
        ],
        [
            Paragraph("<u><b>BANK ACCOUNT NO. :</b></u>", label_u_right_style),
            Paragraph(bank.bank_account_no, cell_left_style),
            Paragraph("<u><b>PACKING NOTE :</b></u>", label_u_style),
            ""
        ],
        [
            Paragraph("<u><b>SWIFT CODE :</b></u>", label_u_right_style),
            Paragraph(bank.swift_code, cell_left_style),
            Paragraph(order.packing_note.upper(), cell_style),
            ""
        ],
        [
            Paragraph("<u><b>INTERMEDIARY BANK :</b></u>", label_u_right_style),
            Paragraph(intermediary, cell_left_style),
            "",
            ""
        ]
    ]

    bank_table = Table(bank_table_data, colWidths=[100, 180, 130, 130])
    bank_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (1, -1), 0.5, colors.black), # Línea vertical divisora entre banco y stickers
        ('LINEAFTER', (1, 0), (1, -1), 0.5, colors.black),
        ('SPAN', (0, 0), (1, 0)),  # OUR BANK DETAILS
        ('SPAN', (2, 0), (3, 0)),  # PALLET & BOX STICKER
        ('SPAN', (2, 1), (3, 1)),  # Label content
        ('SPAN', (2, 2), (3, 2)),  # BOX DESIGN Title
        ('SPAN', (2, 3), (3, 3)),  # Boxes content
        ('SPAN', (2, 4), (3, 4)),  # PACKING NOTE Title
        ('SPAN', (2, 5), (3, 6)),  # Note content (RowSpan 2)
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 6))

    # --- 6. DECLARACIÓN Y FIRMA ---
    declaration_text = "DECLARATION: We declare that this invoice shows the actual price of goods described and all particulars are true and correct."
    
    if sign_stream:
        sign_element = RLImage(sign_stream, width=5.5 * cm, height=1.8 * cm)
        sign_element.hAlign = 'CENTER'
    else:
        sign_element = Paragraph("<b>[ AUTHORIZED SIGNATURE ]</b>", cell_style)

    sign_table_data = [
        [
            Paragraph(declaration_text, cell_style),
            Paragraph("For,", cell_style),
            sign_element
        ],
        [
            "",
            Paragraph(f"<b>{bank.beneficiary}</b>", ParagraphStyle('Ben', fontName='Helvetica-Bold', fontSize=7, alignment=1)),
            ""
        ],
        [
            "",
            Paragraph("Authorized", cell_style),
            ""
        ]
    ]

    sign_table = Table(sign_table_data, colWidths=[240, 140, 160])
    sign_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('SPAN', (0, 0), (0, 2)), # DECLARATION RowSpan 3
        ('SPAN', (2, 0), (2, 2)), # SIGNATURE RowSpan 3
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sign_table)

    return elements