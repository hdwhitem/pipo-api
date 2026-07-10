# src/infrastructure/services/pdf/proforma_type_b/components/header.py
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional
from reportlab.platypus import Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def build_header_component(order, logo_stream: Optional[BytesIO]):
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'HeaderTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        textColor=colors.white, alignment=1
    )
    lbl_style = ParagraphStyle(
        'HeaderLabel', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, alignment=1
    )
    val_style = ParagraphStyle(
        'HeaderValue', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, alignment=1, leading=9
    )

    # Banner del Título
    title_data = [[Paragraph("PROFORMA INVOICE", title_style)]]
    title_table = Table(title_data, colWidths=[567])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
    ]))

    # Carga de Fechas y Datos Truncados
    today_str = datetime.today().strftime("%d/%m/%Y")
    due_date_str = (datetime.today() + timedelta(days=10)).strftime("%d/%m/%Y")

    c_name = order.consignee.name[:45].upper() if len(order.consignee.name) > 45 else order.consignee.name.upper()
    c_addr = order.consignee.address[:40].upper() if len(order.consignee.address) > 40 else order.consignee.address.upper()

    logo_img = Image(logo_stream, width=120, height=40) if logo_stream else Paragraph("", val_style)

    # Columnas de Información
    col1_content = [
        [Paragraph("PI NO.", lbl_style)], [Paragraph(str(order.pi_number), val_style)],
        [Paragraph("DATE", lbl_style)], [Paragraph(today_str, val_style)],
        [Paragraph("DUE DATE", lbl_style)], [Paragraph(due_date_str, val_style)],
        [Paragraph("ORIGIN OF GOODS", lbl_style)], [Paragraph("INDIA", val_style)]
    ]
    col2_content = [
        [Paragraph("CONSIGNEE", lbl_style)],
        [Paragraph(f"{c_name}<br/>{c_addr}<br/>{order.consignee.city}, {order.consignee.country.upper()}<br/>POST CODE: {order.consignee.post_code}<br/>TAX ID: {order.consignee.tax_id}<br/>PH: {order.consignee.phone}", val_style)],
        [Paragraph("TERMS OF DELIVERY & PAYMENT", lbl_style)],
        [Paragraph(f"{order.incoterms.upper()} {order.terms_and_payment.upper()}", val_style)]
    ]
    col3_content = [
        [Paragraph("EXPORTER", lbl_style)],
        [Paragraph(f"{order.exporter.name}<br/>{order.exporter.address}<br/>{order.exporter.city}<br/>POST CODE: {order.exporter.post_code}<br/>TAX ID: {order.exporter.tax_id}<br/>PH: {order.exporter.phone}", val_style)],
        [Paragraph("PORT OF LOADING", lbl_style)],
        [Paragraph("MUNDRA, INDIA", val_style)]
    ]
    col4_content = [
        [logo_img],
        [Paragraph("FINAL DESTINATION", lbl_style)], [Paragraph(order.country_destination.upper(), val_style)],
        [Paragraph("PORT OF DISCHARGE", lbl_style)], [Paragraph(order.port_of_discharge.upper(), val_style)]
    ]

    t1 = Table(col1_content, colWidths=[80])
    t2 = Table(col2_content, colWidths=[160])
    t3 = Table(col3_content, colWidths=[150])
    t4 = Table(col4_content, colWidths=[177])

    for t in [t1, t2, t3, t4]:
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#E0E0E0")),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

    grid_table = Table([[t1, t2, t3, t4]], colWidths=[80, 160, 150, 177])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))

    return [title_table, grid_table]