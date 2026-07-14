# src/infrastructure/services/pdf/proforma_type_a/components/content_a.py

from io import BytesIO
from typing import Dict, List, Optional

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Table, TableStyle, Paragraph, Spacer, Image as RLImage,
)

# ── number-to-words (optional fallback) ──────────────────────────────────
try:
    from src.infrastructure.services.pdf.utils.number_to_words import amount_to_words
except ImportError:
    def amount_to_words(value: float) -> str:
        return f"{value:,.2f} ONLY"

# ── Constants ─────────────────────────────────────────────────────────────
BORDER_W     = 0.3       # 0.1 mm  ≈ 0.28 pt  (data cell borders)
BORDER_OUTER = 0.6       # 0.2 mm  ≈ 0.57 pt  (products table outer)
BORDER_HDR   = 1.0       # 1 pt    (header cells, DefaultCellStyle Border(1))
GREY_L1      = colors.HexColor("#E0E0E0")   # QuestPDF Grey.Lighten1
TOTAL_W      = 567       # A4 usable width (~14 mm margins)

PROD_COLS = [60, 120, 65, 67, 40, 40, 68, 40, 67]

BANK_COLS = [100, 217, 125, 125]

SIGN_COLS = [267, 140, 160]

# ── Paragraph styles ─────────────────────────────────────────────────────
_hdr        = ParagraphStyle("hdr",        fontName="Helvetica-Bold", fontSize=8,  leading=10, alignment=1)
_cell       = ParagraphStyle("cell",       fontName="Helvetica",       fontSize=8,  leading=10, alignment=1)
_cell_bold  = ParagraphStyle("cell_bold",  fontName="Helvetica-Bold", fontSize=9,  leading=11, alignment=1)
_cell_right = ParagraphStyle("cell_right", fontName="Helvetica-Bold", fontSize=8,  leading=10, alignment=2)
_cell_left  = ParagraphStyle("cell_left",  fontName="Helvetica",       fontSize=8,  leading=10, alignment=0)
_total_txt  = ParagraphStyle("total_txt",  fontName="Helvetica-Bold", fontSize=11, leading=15, alignment=1)
_words_lbl  = ParagraphStyle("words_lbl",  fontName="Helvetica-Bold", fontSize=10, leading=12, alignment=0)
_words_val  = ParagraphStyle("words_val",  fontName="Helvetica",       fontSize=8,  leading=10, alignment=1)
_bnk_title  = ParagraphStyle("bnk_title",  fontName="Helvetica-Bold", fontSize=9,  leading=11, alignment=0)
_lbl_right  = ParagraphStyle("lbl_right",  fontName="Helvetica-Bold", fontSize=8,  leading=10, alignment=2)
_lbl_left   = ParagraphStyle("lbl_left",   fontName="Helvetica-Bold", fontSize=8,  leading=10, alignment=0)
_small      = ParagraphStyle("small",      fontName="Helvetica",       fontSize=7,  leading=9,  alignment=1)

# ── Helpers ───────────────────────────────────────────────────────────────
def _fmt(value: float, currency: int) -> str:
    """FormatCurrency: $1,234.56  or  €1,234.56"""
    sym = "$" if currency == 1 else "€"
    return f"{sym}{value:,.2f}"


def _rotate_image(stream: BytesIO) -> Optional[RLImage]:
    """Rotate 90° CW (matching .NET RotateRight) and resize to square."""
    try:
        img = PILImage.open(stream)
        img = img.rotate(270, expand=True)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return RLImage(buf, width=56, height=28)
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════
def build_content_component(
    order,
    slab_images: Dict[str, BytesIO],
    sign_stream: Optional[BytesIO] = None,
) -> List:
    elements: List = []

    # ── Extract order fields ──────────────────────────────────────────────
    slabs        = order.slabs
    currency     = order.currency
    discount     = getattr(order, "discount", 0) or 0
    ocean_freight = getattr(order, "ocean_freight", 0) or 0
    count_20ft   = getattr(order, "container_20ft", 0) or 0
    count_40ft   = getattr(order, "container_40ft", 0) or 0
    hscode       = getattr(order, "hscode_id", "")
    label        = getattr(order, "box_sticker", "REGULAR")
    boxes        = getattr(order, "box_design", "REGULAR")
    note         = getattr(order, "packing_note", "REGULAR")
    bank         = order.bank

    # ════════════════════════════════════════════════════════════════════
    # CALCULATIONS  (matching .NET foreach + summary)
    # ════════════════════════════════════════════════════════════════════
    tot_qty      = 0
    tot_area     = 0.0
    tot_pallets  = 0.0
    tot_subtotal = 0.0

    for s in slabs:
        ps     = s.pallet_slabs if s.pallet_slabs else 1
        pallet = 0.0 if ps == 0 else (20.0 if s.qty == 0 else s.qty / ps)
        area   = s.qty * (s.width * s.height)
        area   = 0.0 if area < 1 else area
        amount = (s.price or 0) * area

        tot_qty      += s.qty
        tot_area     += area
        tot_pallets  += pallet
        tot_subtotal += amount

    total = tot_subtotal - discount + ocean_freight

    # ════════════════════════════════════════════════════════════════════
    # 1. PRODUCTS TABLE
    # ════════════════════════════════════════════════════════════════════
    price_hdr = "PRICE USD FOB" if currency == 1 else "PRICE EUR FOB"
    header_row = [
        Paragraph("SIZE IN MM",             _hdr),
        Paragraph("DESCRIPTION OF THE ITEM", _hdr),
        Paragraph("ITEM IMAGE",              _hdr),
        Paragraph("FINISHING",               _hdr),
        Paragraph("NO. PCS",                 _hdr),
        Paragraph("NO. CRATES",              _hdr),
        Paragraph("SQUARE METER",            _hdr),
        Paragraph(price_hdr,                 _hdr),
        Paragraph("TOTAL AMOUNT",            _hdr),
    ]
    table_data = [header_row]

    for s in slabs:
        ps     = s.pallet_slabs if s.pallet_slabs else 1
        pallet = 0.0 if ps == 0 else (20.0 if s.qty == 0 else s.qty / ps)
        dims   = f"{int(s.width * 1000)}X{int(s.height * 1000)}X{s.thickness}"

        area   = s.qty * (s.width * s.height)
        area   = 0.0 if area < 1 else area
        amount = (s.price or 0) * area

        # ── Image: rotate 90° CW, 1 cm, with 0.1mm border + 0.5mm pad ──
        img_s = slab_images.get(s.image)
        if img_s:
            rot = _rotate_image(img_s)
            if rot:
                img_el = rot
                img_el.hAlign = 'CENTER'
            else:
                img_el = Paragraph("No Image", _small)
        else:
            img_el = Paragraph("No Image", _small)

        table_data.append([
            Paragraph(dims,                           _cell),
            Paragraph(s.name,                         _cell),
            img_el,
            Paragraph(str(s.finished),                _cell),
            Paragraph(str(s.qty),                     _cell),
            Paragraph(f"{pallet:.2f}",                _cell),
            Paragraph(f"{area:.2f}",                  _cell),
            Paragraph(_fmt(s.price or 0, currency),   _cell_bold),
            Paragraph(_fmt(amount, currency),         _cell),
        ])

    # ── Containers string ─────────────────────────────────────────────────
    containers = " "
    if count_20ft == 0 and count_40ft > 0:
        containers = f"{count_40ft}X40FT" if count_40ft > 9 else f"0{count_40ft}X40FT"
    elif count_40ft == 0 and count_20ft > 0:
        containers = f"{count_20ft}X20FT" if count_20ft > 9 else f"0{count_20ft}X20FT"
    elif count_20ft > 0 and count_40ft > 0:
        containers = f"0{count_20ft}X20FT & 0{count_40ft}X40FT"

    # ── Total rows ────────────────────────────────────────────────────────
    n        = len(slabs)
    tr       = n + 1                       # first total row index
    has_disc = discount > 0
    has_frt  = ocean_freight > 0
    has_ex   = has_disc or has_frt
    has_both = has_disc and has_frt


    total_text = f"TOTAL ORDER OF {containers}. HS-CODE: {hscode}."

    # Base total row (Qty / Pallets / Area / empty / Subtotal)
    table_data.append([
        Paragraph(total_text,                              _total_txt),
        "", "", "",
        Paragraph(str(tot_qty),                           _cell_bold),
        Paragraph(f"{tot_pallets:.1f}",                   _cell_bold),
        Paragraph(f"{tot_area:.2f}",                      _cell_bold),
        "",
        Paragraph(_fmt(tot_subtotal, currency),            _cell_bold),
    ])

    # Extra rows
    if has_disc:
        table_data.append(["", "", "", "", "", "",
                           Paragraph("Discount", _cell_right), "",
                           Paragraph(_fmt(discount, currency), _cell_bold)])
    if has_frt:
        table_data.append(["", "", "", "", "", "",
                           Paragraph("Ocean Freight", _cell_right), "",
                           Paragraph(_fmt(ocean_freight, currency), _cell_bold)])
    if has_ex:
        table_data.append(["", "", "", "", "", "",
                           Paragraph("Grand Total", _cell_right), "",
                           Paragraph(_fmt(total, currency), _cell_bold)])

    # ── Build + style products table ──────────────────────────────────────
    prod_tbl = Table(table_data, colWidths=PROD_COLS)

    style = [
        # Outer border 0.2 mm
        ("BOX", (0, 0), (-1, -1), BORDER_OUTER, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), GREY_L1),
        ("INNERGRID", (0, 1), (-1, n), BORDER_W, colors.black),
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 1),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 1),
    ]

    # Total row styling
    if has_both:
        # RowSpan 4 on TOTAL ORDER text
        style.extend([
            ("SPAN",       (0, tr), (3, tr + 3)),
            ("BACKGROUND", (0, tr), (-1, tr + 3), GREY_L1),
            ("LINEABOVE",  (4, tr), (6, tr), 1, colors.black),
        ])
        # SPANs for label columns in extra rows
        er = tr + 1
        if has_disc:
            style.append(("SPAN", (6, er), (7, er)))
            er += 1
        if has_frt:
            style.append(("SPAN", (6, er), (7, er)))
            er += 1
        # Grand Total row
        style.extend([
            ("SPAN",       (6, er), (7, er)),
            ("LINEBELOW",  (0, er), (5, er), 1, colors.black),
        ])
    elif has_ex:
        # RowSpan 3
        style.extend([
            ("SPAN",       (0, tr), (3, tr + 2)),
            ("BACKGROUND", (0, tr), (-1, tr + 2), GREY_L1),
        ])
        er = tr + 1
        if has_disc:
            style.append(("SPAN", (6, er), (7, er)))
            er += 1
        if has_frt:
            style.append(("SPAN", (6, er), (7, er)))
            er += 1
        style.extend([
            ("SPAN",      (6, er), (7, er)),
        ])
    else:
        # ColumnSpan 4, no RowSpan
        style.extend([
            ("SPAN",       (0, tr), (3, tr)),
            ("BACKGROUND", (0, tr), (-1, tr), GREY_L1),
        ])

    prod_tbl.setStyle(TableStyle(style))
    elements.append(prod_tbl)
    elements.append(Spacer(1, 9))

    words = amount_to_words(total).upper()

    words_tbl = Table(
        [[Paragraph("<b><u>AMOUNT CHARGEABLE IN WORDS :</u></b>", _words_lbl)],
         [Paragraph(words, _words_val)]],
        colWidths=[TOTAL_W],
    )
    words_tbl.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), BORDER_W, colors.black),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.white),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(words_tbl)
    elements.append(Spacer(1, 9))

    currency_str = "USD DOLLAR ($)" if currency == 1 else "EUR EURO (€)"
    intermediary = "NA" if currency == 2 else (getattr(bank, "intermediary_bank", "") or "")

    bank_data = [
        # Row 0 — Header
        [Paragraph("<b><u>OUR BANK DETAILS :</u></b>", _bnk_title),
         "",
         Paragraph("<b><u>PALLET &amp; BOX STICKER :</u></b>", _lbl_left),
         ""],
        # Row 1 — BENEFICIARY NAME | value | sticker value
        [Paragraph("<b><u> BENEFICIARY NAME :</u></b>", _lbl_right),
         Paragraph(str(bank.beneficiary), _cell_left),
         Paragraph(label.upper(), _cell),
         ""],
        # Row 2 — BANK NAME | value | BOX DESIGN label
        [Paragraph("<b><u>BANK NAME :</u></b>", _lbl_right),
         Paragraph(str(bank.bank_name), _cell_left),
         Paragraph("<b><u>BOX DESIGN :</u></b>", _lbl_left),
         ""],
        # Row 3 — CURRENCY ACCOUNT | value | boxes value
        [Paragraph("<b><u>CURRENCY ACCOUNT :</u></b>", _lbl_right),
         Paragraph(currency_str, _cell_left),
         Paragraph(boxes.upper(), _cell),
         ""],
        # Row 4 — BANK ACCOUNT NO. | value | PACKING NOTE label
        [Paragraph("<b><u>BANK ACCOUNT NO. :</u></b>", _lbl_right),
         Paragraph(str(bank.bank_account_no), _cell_left),
         Paragraph("<b><u>PACKING NOTE :</u></b>", _lbl_left),
         ""],
        # Row 5 — SWIFT CODE | value | note (rowspan 2)
        [Paragraph("<b><u>SWIFT CODE :</u></b>", _lbl_right),
         Paragraph(str(bank.swift_code), _cell_left),
         Paragraph(note.upper(), _cell),
         ""],
        # Row 6 — INTERMEDIARY BANK | value | (part of note rowspan)
        [Paragraph("<b><u>INTERMEDIARY BANK :</u></b>", _lbl_right),
         Paragraph(intermediary, _cell_left),
         "",
         ""],
    ]

    bank_tbl = Table(bank_data, colWidths=BANK_COLS)
    bank_tbl.setStyle(TableStyle([
        # Outer border 0.1 mm
        ("BOX", (0, 0), (-1, -1), BORDER_W, colors.black),
        # Vertical divider between bank cols and sticker cols
        ("LINEAFTER", (1, 0), (1, -1), BORDER_W, colors.black),
        # Header SPANs
        ("SPAN", (0, 0), (1, 0)),       # OUR BANK DETAILS
        ("SPAN", (2, 0), (3, 0)),       # PALLET & BOX STICKER
        # Right-side SPANs (matching .NET ColumnSpan(2))
        ("SPAN", (2, 1), (3, 1)),       # sticker value
        ("SPAN", (2, 2), (3, 2)),       # BOX DESIGN label
        ("SPAN", (2, 3), (3, 3)),       # boxes value
        ("SPAN", (2, 4), (3, 4)),       # PACKING NOTE label
        ("SPAN", (2, 5), (3, 6)),       # note value (RowSpan 2)
        # Alignment & padding
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(bank_tbl)
    elements.append(Spacer(1, 9))

    decl = "DECLARATION: We declare that this invoice shows the actual price of goods described and all particulars are true and correct."

    if sign_stream:
        try:
            sign_stream.seek(0)
            sign_el = RLImage(BytesIO(sign_stream.getvalue()), width=150, height=30)
            sign_el.hAlign = "CENTER"
        except Exception:
            sign_el = Paragraph("[SIGNATURE]", _small)
    else:
        sign_el = Paragraph("[SIGNATURE]", _small)

    sign_data = [
        [Paragraph(decl,                              _cell),
         Paragraph("For,",                             _cell),
         sign_el],
        ["",
         Paragraph(str(bank.beneficiary),              _small),
         ""],
        ["",
         Paragraph("Authorized",                       _cell),
         ""],
    ]

    sign_tbl = Table(sign_data, colWidths=SIGN_COLS)
    sign_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), BORDER_W, colors.black),
        ("LINEAFTER", (0, 0), (1, -1), BORDER_W, colors.black),
        
        ("SPAN", (0, 0), (0, 2)),   # Declaration
        ("SPAN", (2, 0), (2, 2)),   # Sign image
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
    ]))
    elements.append(sign_tbl)

    return elements