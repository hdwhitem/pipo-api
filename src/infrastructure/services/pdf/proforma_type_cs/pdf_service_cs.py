# src/infrastructure/services/pdf/pdf_service.py
import httpx
from io import BytesIO
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Spacer

from src.core.config import settings
from src.infrastructure.services.pdf.proforma_type_cs.components.header_cs import build_header_component
from src.infrastructure.services.pdf.proforma_type_cs.components.content_cs import build_content_component
from src.infrastructure.services.pdf.common.footer import NumberedCanvas
from src.infrastructure.services.pdf.utils.image_fetcher import fetch_image_bytes


class ProformaTypeCSBuilder:

    @classmethod
    async def generate_proforma_invoice_cs(cls, order) -> bytes:
        buffer = BytesIO()
        
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=14,
            rightMargin=14,
            topMargin=14,
            bottomMargin=25  # Espacio para el footer
        )

        # 1. Carga Asíncrona de Imágenes
        async with httpx.AsyncClient() as client:
            logo_stream = await fetch_image_bytes(client, order.supplier.logo)
            sign_stream = await fetch_image_bytes(client, getattr(order, 'sign_url', ''))
            
            slab_images: Dict[str, BytesIO] = {}
            for slab in order.slabs:
                img_url = f"{settings.CLOUDINARY_BASE_URL}/{slab.image}"
                slab_images[slab.image] = await fetch_image_bytes(client, img_url)

        # 2. Construcción del Story
        elements = [
            *build_header_component(order, logo_stream),
            Spacer(1, 10),
            *build_content_component(order, slab_images, sign_stream)
        ]

        # 3. Asignación del Frame y Template
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='ProformaTemplate', frames=frame)
        doc.addPageTemplates([template])

        # 4. Render pasándole NumberedCanvas en canvasmaker
        doc.build(elements, canvasmaker=NumberedCanvas)
        
        return buffer.getvalue()