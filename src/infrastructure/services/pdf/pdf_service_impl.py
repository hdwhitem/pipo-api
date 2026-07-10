from src.application.interfaces.ipdf_service import IPdfService
from src.domain.models.order import Order
from src.infrastructure.services.pdf.proforma_type_a.pdf_service_a import ProformaTypeABuilder
from src.infrastructure.services.pdf.proforma_type_cs.pdf_service_cs import ProformaTypeCSBuilder


class PdfService(IPdfService):
    
    async def generate_proforma_a(self, order: Order) -> bytes:
        return await ProformaTypeABuilder.generate_proforma_invoice_a(order)

    async def generate_proforma_cs(self, order: Order) -> bytes:
        return await ProformaTypeCSBuilder.generate_proforma_invoice_cs(order)


def get_pdf_service() -> IPdfService:
    """Inyector de dependencia para FastAPI."""
    return PdfService()