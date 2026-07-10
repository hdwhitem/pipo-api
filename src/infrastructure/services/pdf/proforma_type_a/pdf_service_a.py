# src/infrastructure/services/pdf/proforma_type_b/builder.py
import httpx
from io import BytesIO
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Spacer

from src.core.config import settings
from src.infrastructure.services.pdf.common.footer import NumberedCanvas
from src.infrastructure.services.pdf.utils.image_fetcher import fetch_image_bytes
from src.infrastructure.services.pdf.proforma_type_a.components.header_a import build_header_component
from src.infrastructure.services.pdf.proforma_type_a.components.content_a import build_table_content_component


class ProformaTypeABuilder:

    @classmethod
    async def generate_proforma_invoice_a(cls, order) -> bytes:
        buffer = BytesIO()

        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=14,
            rightMargin=14,
            topMargin=14,
            bottomMargin=25
        )

        # 1. Recuperar assets e imágenes
        async with httpx.AsyncClient() as client:
            logo_stream = await fetch_image_bytes(client, order.supplier.logo)
            sign_stream = await fetch_image_bytes(client, getattr(order, 'sign_url', ''))

            slab_images: Dict[str, BytesIO] = {}
            for slab in order.slabs:
                img_url = f"{settings.CLOUDINARY_BASE_URL}/{slab.image}"
                slab_images[slab.image] = await fetch_image_bytes(client, img_url)

        # 2. Ensamblar los componentes
        story = []
        story.extend(build_header_component(order, logo_stream))
        story.append(Spacer(1, 10))

        story.extend(build_table_content_component(
            slabs=order.slabs,
            sign_stream=sign_stream,
            discount=order.discount,
            count20ft=order.container_20ft,
            count40ft=order.container_40ft,
            currency=order.currency,
            label=order.box_sticker,
            boxes=order.box_design,
            note=order.packing_note,
            ocean_freight=order.ocean_freight,
            gbank_account=order.bank,
            hscode=order.hscode_id,
            slab_images=slab_images
        ))

        # 3. Configurar plantilla con el Canvas estandarizado
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='ProformaTypeBTemplate', frames=frame)
        doc.addPageTemplates([template])

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()