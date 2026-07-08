from fastapi import APIRouter, Response, Request, status
from src.application.interfaces.ipdf_service import IPdfService
from src.domain.dtos.pdf_report_dto import SimpleReportDto

router = APIRouter(prefix="/api/Pdf", tags=["PDF Reports"])

@router.post(
    "/generate-sample", 
    status_code=status.HTTP_200_OK,
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Retorna el reporte en formato PDF."
        }
    }
)
def generate_sample_pdf(dto: SimpleReportDto, request: Request):
    pdf_service: IPdfService = request.app.state.pdf_service
    pdf_bytes = pdf_service.generate_sample_report(dto)
    
    filename = f"Report_{dto.pi_number}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )