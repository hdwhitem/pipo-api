from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional
from reportlab.platypus import Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def build_header_component(order, logo_stream: Optional[BytesIO]):
    styles = getSampleStyleSheet()
    grey = colors.HexColor("#E0E0E0")

    # ── Styles ──────────────────────────────────────────────
    s_title = ParagraphStyle(
        'Title', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        textColor=colors.white, alignment=1
    )
    s_lbl_lg = ParagraphStyle(
        'LblLg', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, alignment=1, leading=11
    )
    s_lbl = ParagraphStyle(
        'Lbl', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, alignment=1, leading=9
    )
    s_val_lg = ParagraphStyle(
        'ValLg', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, alignment=1, leading=11
    )
    s_val = ParagraphStyle(
        'Val', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, alignment=1, leading=10
    )
    
    s_val_ce = ParagraphStyle(
        'Val', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, alignment=1, leading=12
    )

    # ── Title Banner ────────────────────────────────────────
    title_tbl = Table(
        [[Paragraph("PROFORMA INVOICE", s_title)]],
        colWidths=[567]
    )
    title_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
    ]))

    # ── Data ────────────────────────────────────────────────
    today_str = datetime.today().strftime("%d/%m/%Y")
    due_str = (datetime.today() + timedelta(days=10)).strftime("%d/%m/%Y")

    c_name = (
        order.consignee.name[:45]
        if len(order.consignee.name) > 45
        else order.consignee.name
    ).upper()
    c_addr = (
        order.consignee.address[:40]
        if len(order.consignee.address) > 40
        else order.consignee.address
    ).upper()

    logo = (
        Image(logo_stream, width=118, height=60)
        if logo_stream
        else Paragraph("", s_val)
    )

    consignee_block = (
        f"{c_name}<br/>"
        f"{c_addr}<br/>"
        f"{order.consignee.city}, {order.consignee.country.upper()}<br/>"
        f"POST CODE: {order.consignee.post_code}<br/>"
        f"TAX ID: {order.consignee.tax_id}<br/>"
        f"PH: {order.consignee.phone}"
    )
    exporter_block = (
        f"{order.exporter.name}<br/>"
        f"{order.exporter.address}<br/>"
        f"{order.exporter.city}<br/>"
        f"POST CODE: {order.exporter.post_code}<br/>"
        f"TAX ID: {order.exporter.tax_id}<br/>"
        f"PH: {order.exporter.phone}"
    )

    c1w, c2w, c3w, c4w = 79, 213, 155, 120

    terms_text = f"{order.incoterms.upper()} - {order.terms_and_payment.upper()}"

    # ── Tabla unificada: 4 columnas × 9 filas ─────────────
    data = [
        # Row 0
        [
            Paragraph("PI NO.", s_lbl_lg),
            Paragraph("CONSIGNEE", s_lbl_lg),
            Paragraph("EXPORTER", s_lbl_lg),
            logo,
        ],
        # Row 1
        [
            Paragraph(str(order.pi_number), s_val_lg),
            Paragraph(consignee_block, s_val_ce),
            Paragraph(exporter_block, s_val_ce),
            "",
        ],
        # Row 2
        [Paragraph("DATE", s_lbl), "", "", ""],
        # Row 3
        [Paragraph(today_str, s_val), "", "", ""],
        # Row 4
        
        # Row 5
        [
            Paragraph("DUE DATE", s_lbl),
            "",
            "",
            Paragraph("FINAL DESTINATION", s_lbl),
        ],
        # Row 6
        [
            Paragraph(due_str, s_val),
            "",
            "",
            Paragraph(order.country_destination.upper(), s_val), # Valor destino
        ],
        # Row 7 (Corregido índice de comentarios)
        [
            Paragraph("ORIGIN OF GOODS", s_lbl),
            Paragraph("TERMS OF DELIVERY & PAYMENT", s_lbl),
            Paragraph("PORT OF LOADING", s_lbl),
            Paragraph("PORT OF DISCHARGE", s_lbl),
        ],
        # Row 8 - Corregido para mapear correctamente las columnas de la tabla
        [
            Paragraph("INDIA", s_val),
            Paragraph(terms_text, s_val),                          # Términos en Col 1
            Paragraph("MUNDRA, INDIA", s_val),                     # Port of Loading en Col 2
            Paragraph(order.port_of_discharge.upper(), s_val),     # Port of Discharge en Col 3
        ],
    ]

    tbl = Table(data, colWidths=[c1w, c2w, c3w, c4w])
    tbl.setStyle(TableStyle([
        # ── SPANs ──
        ('SPAN', (1, 1), (1, 5)),    # Consignee: filas 1 a 6
        ('SPAN', (2, 1), (2, 5)),    # Exporter: filas 1 a 6
        ('SPAN', (3, 0), (3, 3)),    # Logo: filas 0 a 4
        ('SPAN', (0, 6), (0, 6)),    # INDIA ocupa fila 7 y 8 en col 0
       

        # ── Fondos grises ──
        ('BACKGROUND', (0, 0), (2, 0), grey),    # PI NO, CONSIGNEE, EXPORTER
        ('BACKGROUND', (0, 2), (0, 2), grey),    # DATE
        ('BACKGROUND', (0, 4), (0, 4), grey),    # DUE DATE
        ('BACKGROUND', (3, 4), (3, 4), grey),    # FINAL DESTINATION
        ('BACKGROUND', (0, 6), (3, 6), grey),    # TERMS, PORT LOADING, DISCHARGE labels

        # ── Grid unificado ──
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),

        # ── Alineación ──
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # ── Padding ──
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
    ]))

    return [title_tbl, tbl]