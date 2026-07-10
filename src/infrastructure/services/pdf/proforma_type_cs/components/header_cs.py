# src/infrastructure/services/pdf/components/header.py
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image as RLImage


def build_header_component(order, logo_stream: Optional[BytesIO]) -> List:
    elements = []
    
    # --- 1. ESTILOS ---
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'HeaderTitle',
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1, # Center
        textColor=colors.black
    )
    
    label_style = ParagraphStyle(
        'HeaderLabel',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10
    )
    
    label_lg_style = ParagraphStyle(
        'HeaderLabelLg',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12
    )
    
    val_style = ParagraphStyle(
        'HeaderValue',
        fontName='Helvetica',
        fontSize=8,
        alignment=1, # Center
        leading=10
    )
    
    val_bold_style = ParagraphStyle(
        'HeaderValueBold',
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=1, # Center
        leading=13
    )

    # --- 2. TÍTULO "PROFORMA INVOICE" ---
    title_table = Table([[Paragraph("PROFORMA INVOICE", title_style)]], colWidths=['100%'])
    title_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(title_table)

    # --- 3. LOGO ---
    if logo_stream:
        # 9cm de ancho como en el C#
        logo_img = RLImage(logo_stream, width=9 * cm, height=2.5 * cm) 
        logo_img.hAlign = 'CENTER'
        logo_content = logo_img
    else:
        logo_content = Paragraph("<b>NO LOGO</b>", val_style)

    logo_table = Table([[logo_content]], colWidths=['100%'])
    logo_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(logo_table)

    # --- 4. PREPARACIÓN DE DATOS DE LAS 3 COLUMNAS ---
    
    # Helper rápido para construir las celdas internas limpiamente
    def p_label(text: str, is_large: bool = False) -> Paragraph:
        style = label_lg_style if is_large else label_style
        return Paragraph(f"<u><b>{text}</b></u>", style)

    def p_val(text: str, is_bold: bool = False) -> Paragraph:
        style = val_bold_style if is_bold else val_style
        return Paragraph(str(text or ''), style)

    # A. COLUMNA 1: EXPORTER
    exporter_data = [
        [p_label("EXPORTER :", is_large=True)],
        [p_val(order.exporter.name)],
        [p_val(order.exporter.address)],
        [p_val(order.exporter.city)],
        [p_val(f"POST CODE: {order.exporter.post_code}")],
        [p_val(f"TAX ID: {order.exporter.tax_id}")],
        [p_val(f"PH: {order.exporter.phone}")],
        [p_label("PORT OF LOADING :")],
        [p_val("MUNDRA, INDIA")]
    ]
    
    # B. COLUMNA 2: CONSIGNEE (Con recortes de máximo 50 caracteres)
    cons_name = (order.consignee.name[:50] if len(order.consignee.name) > 50 else order.consignee.name).upper()
    cons_addr = (order.consignee.address[:50] if len(order.consignee.address) > 50 else order.consignee.address).upper()
    
    consignee_data = [
        [p_label("CONSIGNEE : ", is_large=True)],
        [p_val(cons_name)],
        [p_val(cons_addr)],
        [p_val(f"{order.consignee.city}, {order.consignee.country.upper()}")],
        [p_val(f"POST CODE: {order.consignee.post_code}")],
        [p_val(f"TAX ID: {order.consignee.tax_id}")],
        [p_val(f"PH: {order.consignee.phone}")],
        [p_label("TERMS OF DELIVERY & PAYMENT :")],
        [p_val(f"{order.incoterms.upper()} {order.terms_and_payment.upper()}")]
    ]

    # C. COLUMNA 3: PI INFO & DATES
    today = datetime.today()
    valid_until = today + timedelta(days=15)
    today_str = today.strftime("%d/%m/%Y")
    valid_until_str = valid_until.strftime("%d/%m/%Y")

    pi_info_data = [
        [p_label("PI NO. :", is_large=True)],
        [p_val(f"{order.pi_number} / {today.year}", is_bold=True)],
        [p_label("VALID DATE :")],
        [p_val(f"{today_str} TO {valid_until_str}")],
        [p_label("FINAL DESTINATION :")],
        [p_val(order.country_destination.upper())],
        [p_label("PORT OF DISCHARGE :")],
        [p_val(order.port_of_discharge.upper())]
    ]

    # Sub-tablas con estilos para simular la línea divisora interna (`BorderTop`)
    col1_table = Table(exporter_data, colWidths=['100%'])
    col1_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 7), (-1, 7), 0.5, colors.black), # Línea en PORT OF LOADING
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    col2_table = Table(consignee_data, colWidths=['100%'])
    col2_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 7), (-1, 7), 0.5, colors.black), # Línea en TERMS OF DELIVERY
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    col3_table = Table(pi_info_data, colWidths=['100%'])
    col3_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 6), (-1, 6), 0.5, colors.black), # Línea en PORT OF DISCHARGE
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    # --- 5. TABLA CONTENEDORA DE LAS 3 COLUMNAS ---
    # Ancho A4 imprimible = ~19cm (5.5cm + 8cm + 5.5cm)
    columns_table = Table([[col1_table, col2_table, col3_table]], colWidths=[5.5 * cm, 8 * cm, 5.5 * cm])
    columns_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    elements.append(columns_table)
    return elements