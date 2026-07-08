from abc import ABC, abstractmethod
from src.domain.dtos.pdf_report_dto import SimpleReportDto

class IPdfService(ABC):
    
    @abstractmethod
    def generate_sample_report(self, data: SimpleReportDto) -> bytes:
        """Genera un reporte PDF simple en memoria y retorna sus bytes."""
        pass