from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from src.domain.collections.gorder import GOrder
from src.domain.models.order import Order
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_pdf_service(request: Request):
    """Extrae la instancia de PdfService configurada en main.py"""
    return request.app.state.pdf_service


@router.post(
    "/ProformaInvoice",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Retorna la Proforma Invoice en formato PDF."
        }
    }
)
async def proforma_invoice(
    parameters: GOrder,
    request: Request,
    pdf_service = Depends(get_pdf_service),
    user_session: dict = Depends(verify_authorize)
) -> Response:
    if parameters is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Parameters are required"
        )

    mongo_repo: IMongoRepo = request.app.state.repo

    # 1. Gestión de PI Number
    pi = 0
    if not parameters.pi_number:
        pi = await mongo_repo.get_proforma_number()
        parameters.pi_number = pi
        save_pi = await mongo_repo.save_order(parameters)
        if save_pi is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        pi = await mongo_repo.update_pi_number(int(parameters.pi_number))
        save_pi = await mongo_repo.save_order(parameters)
        if save_pi is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # 2. Obtención de Entidades Relacionadas desde Mongo
    consignee = await mongo_repo.get_consignee_by_id(parameters.consignee_id)
    if consignee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consignee not found")

    supplier = await mongo_repo.get_supplier_by_id(parameters.supplier_id)
    exporter = await mongo_repo.get_exporter_by_id(supplier.exporter_id)
    bank = await mongo_repo.get_bank_account_by_id(exporter.bank_id)

    # 3. Construcción del Objeto Order
    order = Order(
        pi_number=pi,
        currency=parameters.currency,
        country_destination=parameters.country_destination,
        port_of_discharge=parameters.port_of_discharge,
        terms_and_payment=parameters.terms_and_payment,
        incoterms=parameters.incoterms,
        container_20ft=parameters.container20ft,
        container_40ft=parameters.container40ft,
        box_sticker=parameters.box_sticker,
        box_design=parameters.box_design,
        packing_note=parameters.packing_note,
        consignee=consignee,
        discount=parameters.discount,
        ocean_freight=parameters.ocean_freight,
        supplier=supplier,
        hscode_id=parameters.hscode_id,
        exporter=exporter,
        bank=bank,
        slabs=parameters.slab,
    )

    # 4. Generación dinámica de la Proforma (Esperando los bytes con await)
    if parameters.supplier_id == "8":
        pdf_bytes = await pdf_service.generate_proforma_cs(order)
    else:
        pdf_bytes = await pdf_service.generate_proforma_a(order)

    filename = f"Proforma_Invoice_{pi}.pdf"

    # 5. Respuesta HTTP exacta a la versión anterior que funcionaba
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )