from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado de 2 pasadas para calcular el número total de páginas 
    y dibujar el footer estandarizado en todos los reportes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7)
        self.setFillColor(colors.HexColor("#555555"))

        # Dimensiones de página A4 portrait
        page_width = 595.27
        y = 12

        # 1. Izquierda: Mensaje legal / Aviso
        self.drawString(14, y, "THIS PROFORMA IS NOT VALID FOR PAYMENT PURPOSES")

        # 2. Centro: Fecha y hora de generación
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.drawCentredString(page_width / 2.0, y, f"Generated on: {date_str}")

        # 3. Derecha: Paginación dinamicamente calculada
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_width - 14, y, page_text)

        self.restoreState()