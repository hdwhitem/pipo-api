from abc import ABC, abstractmethod
from src.domain.models.order import Order


class IPdfService(ABC):
    """Interfaz abstracta para el servicio de generación de PDFs."""

    @abstractmethod
    async def generate_proforma_a(self, order: Order) -> bytes:
        """Genera el PDF para la Proforma Tipo A (Estándar)."""
        pass

    @abstractmethod
    async def generate_proforma_cs(self, order: Order) -> bytes:
        """Genera el PDF para la Proforma Tipo CS (Slabs / Detallada)."""
        pass