# src/infrastructure/services/pdf/proforma_type_a/components/header_cs.py
"""
Header component matching .NET 8 QuestPDF HeaderContentCS exactly.

.NET layout (3 visual rows stacked vertically):
  Row 1  - Full-width: "PROFORMA INVOICE" (centered, fontSize=10, SemiBold, underlined)
  Row 2  - Full-width: Logo image (centered, 9 cm wide)
  Row 3  - Three bordered columns side-by-side (single table, same height):
              Col 1 (5.5 cm)  EXPORTER  + PORT OF LOADING
              Col 2 (relative) CONSIGNEE + TERMS OF DELIVERY & PAYMENT
              Col 3 (5.5 cm)  PI NO / VALID DATE / FINAL DESTINATION / PORT OF DISCHARGE

Labels are SemiBold + Underline, LEFT-aligned (matching .NET default).
Values are CENTER-aligned (matching .NET .AlignCenter()).
"""
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Table, TableStyle, Paragraph, Image, HRFlowable,
)

# ── Constants ─────────────────────────────────────────────────────────────
BORDER_W = 0.3                       # 0.1 mm ≈ 0.28 pt → 0.3 pt
TOTAL_W  = 567                       # A4 usable width with ~14 mm margins
COL1_W   = 5.5 * cm                  # Exporter   ≈ 155.9 pt
COL3_W   = 5.5 * cm                  # PI Info    ≈ 155.9 pt
COL2_W   = TOTAL_W - COL1_W - COL3_W  # Consignee ≈ 255.2 pt

# ── Paragraph styles ─────────────────────────────────────────────────────

_title_label_lg = ParagraphStyle(
    "lbl_lg", fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=colors.black, alignment=1,
)
_label_lg = ParagraphStyle(
    "lbl_lg", fontName="Helvetica-Bold", fontSize=10, leading=14,
    textColor=colors.black, alignment=0,
)
_label_md = ParagraphStyle(
    "lbl_sm", fontName="Helvetica-Bold", fontSize=9, leading=14,
    textColor=colors.black, alignment=0,
)
_label_sm = ParagraphStyle(
    "lbl_sm", fontName="Helvetica-Bold", fontSize=9, leading=13,
    textColor=colors.black, alignment=0,
)
# Values → CENTER-aligned (matching .NET .AlignCenter() on value items)
_val_lg = ParagraphStyle(
    "val_lg", fontName="Helvetica-Bold", fontSize=11, leading=15.5,
    textColor=colors.black, alignment=1,
)
_val_lg2 =ParagraphStyle(
    "val_md", fontName="Helvetica", fontSize=9, leading=14,
    textColor=colors.black, alignment=1,
)
_val_md = ParagraphStyle(
    "val_md", fontName="Helvetica", fontSize=9, leading=11,
    textColor=colors.black, alignment=1,
)
_val_sm = ParagraphStyle(
    "val_sm", fontName="Helvetica", fontSize=8, leading=12,
    textColor=colors.black, alignment=1,
)
_val_xs = ParagraphStyle(
    "val_sm", fontName="Helvetica", fontSize=8, leading=10,
    textColor=colors.black, alignment=1,
)

# ── Helpers ───────────────────────────────────────────────────────────────
def _sep():
    """Horizontal rule replicating .NET's .BorderTop(0.1f, Unit.Millimetre)."""
    return HRFlowable(width="100%", thickness=BORDER_W, color=colors.black)


# ══════════════════════════════════════════════════════════════════════════
def build_header_component(order, logo_stream: Optional[BytesIO]) -> List:
    """
    Replicate .NET HeaderContentCS.Compose() in ReportLab.

    Parameters
    ----------
    order : Order-like object with .pi_number, .incoterms, .terms_and_payment,
            .country_destination, .port_of_discharge, .consignee.*, .exporter.*
    logo_stream : BytesIO  (PNG/JPG bytes for the company logo)
    """

    # ── Dates ─────────────────────────────────────────────────────────────
    today    = datetime.today()
    today_s  = today.strftime("%d/%m/%Y")
    due_s    = (today + timedelta(days=15)).strftime("%d/%m/%Y")

    # ── Truncate consignee name / address to 50 chars (matching .NET) ────
    c_name = (order.consignee.name[:50] if len(order.consignee.name) > 50
              else order.consignee.name).upper()
    c_addr = (order.consignee.address[:50] if len(order.consignee.address) > 50
              else order.consignee.address).upper()

    # =====================================================================
    # ROW 1 - "PROFORMA INVOICE" title
    # =====================================================================
    title_tbl = Table(
        [[Paragraph("<b>PROFORMA INVOICE</b>", _title_label_lg)]],
        colWidths=[TOTAL_W],
    )
    title_tbl.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), BORDER_W, colors.black),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.white),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    # =====================================================================
    # ROW 2 - Logo (centered, 9 cm wide)
    # =====================================================================
    if logo_stream and hasattr(logo_stream, "read"):
        logo_stream.seek(0)
        logo_img = Image(logo_stream, width=9 * cm, height=1.5 * cm * 0.45)
    else:
        logo_img = Paragraph("", _val_sm)

    logo_tbl = Table(
        [[logo_img]],
        colWidths=[TOTAL_W],
    )
    logo_tbl.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), BORDER_W, colors.black),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.white),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    # =====================================================================
    # ROW 3 - Single 3-column table
    # BOX gives outer border, LINEAFTER gives vertical column separators.
    # All 3 cells share the same row height → columns end flush together.
    # =====================================================================

    # ── COLUMN 1: EXPORTER (5.5 cm) + PORT OF LOADING ────────────────────
    exporter_content = [
        Paragraph("<b><u>EXPORTER :</u></b>", _label_lg),
        Paragraph(str(order.exporter.name), _val_sm),
        Paragraph(str(order.exporter.address), _val_sm),
        Paragraph(str(order.exporter.city), _val_sm),
        Paragraph(f"POST CODE: {order.exporter.post_code}", _val_sm),
        Paragraph(f"TAX ID: {order.exporter.tax_id}", _val_sm),
        Paragraph(f"PH: {order.exporter.phone}", _val_sm),
        _sep(),
        Paragraph("<b><u>PORT OF LOADING :</u></b>", _label_sm),
        Paragraph("MUNDRA, INDIA", _val_xs),
    ]

    # ── COLUMN 2: CONSIGNEE (relative) + TERMS ───────────────────────────
    consignee_content = [
        Paragraph("<b><u>CONSIGNEE :</u></b>", _label_lg),
        Paragraph(c_name, _val_sm),
        Paragraph(c_addr, _val_sm),
        Paragraph(
            f"{order.consignee.city}, {order.consignee.country.upper()}",
            _val_sm,
        ),
        Paragraph(f"POST CODE: {order.consignee.post_code}", _val_sm),
        Paragraph(f"TAX ID: {order.consignee.tax_id}", _val_sm),
        Paragraph(f"PH: {order.consignee.phone}", _val_sm),
        _sep(),
        Paragraph("<b><u>TERMS OF DELIVERY &amp; PAYMENT :</u></b>", _label_sm),
        Paragraph(
            f"{order.incoterms.upper()} {order.terms_and_payment.upper()}",
            _val_xs,
        ),
    ]

    # ── COLUMN 3: PI NO / VALID DATE / FINAL DEST / PORT DISCH (5.5 cm) ─
    pi_content = [
        Paragraph("<b><u>PI NO. :</u></b>", _label_lg),
        Paragraph(f"{order.pi_number} / {today.year}", _val_lg),
        Paragraph("<b><u>VALID DATE :</u></b>", _label_md),
        Paragraph(f"{today_s} TO {due_s}", _val_lg2),
        Paragraph("<b><u>FINAL DESTINATION :</u></b>", _label_md),
        Paragraph(str(order.country_destination).upper(), _val_lg2),
        _sep(),
        Paragraph("<b><u>PORT OF DISCHARGE :</u></b>", _label_sm),
        Paragraph(str(order.port_of_discharge).upper(), _val_xs),
    ]

    # ── Single table: BOX (outer) + LINEAFTER (vertical separators) ───────
    info_tbl = Table(
        [[exporter_content, consignee_content, pi_content]],
        colWidths=[COL1_W, COL2_W, COL3_W],
    )
    info_tbl.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), BORDER_W, colors.black),
        ("LINEAFTER",    (0, 0), (1, -1),  BORDER_W, colors.black),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.white),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    return [title_tbl, logo_tbl, info_tbl]