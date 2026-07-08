from fpdf import FPDF
from datetime import date
from src.application.interfaces.ipdf_service import IPdfService
from src.domain.dtos.pdf_report_dto import SimpleReportDto

class ReportPDFLayout(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "PROFORMA INVOICE REPORT", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, f"Date: {date.today().strftime('%d/%m/%Y')}", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=8)
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}} - Generated automatically", align="C")


class PdfService(IPdfService):
    def generate_sample_report(self, data: SimpleReportDto) -> bytes:
        pdf = ReportPDFLayout(orientation="P", unit="mm", format="A4")
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Datos del cliente
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Customer Details", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, f"Customer Name: {data.name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Proforma Invoice N°: {data.pi_number}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Encabezado de la Tabla
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 230, 230)
        
        pdf.cell(60, 8, "Item / Parameter", border=1, fill=True)
        pdf.cell(60, 8, "Quantity (QTY)", border=1, fill=True, align="C")
        pdf.cell(60, 8, "Total Amount ($)", border=1, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

        # Contenido de la Tabla
        pdf.set_font("Helvetica", size=10)
        pdf.cell(60, 8, "Order Summary", border=1)
        pdf.cell(60, 8, str(data.qty), border=1, align="C")
        pdf.cell(60, 8, f"${data.total:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        
        # Total
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(120, 8, "GRAND TOTAL", border=1, align="R")
        pdf.cell(60, 8, f"${data.total:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

        return bytes(pdf.output())