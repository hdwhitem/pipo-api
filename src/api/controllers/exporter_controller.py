from fastapi import APIRouter, Depends, Request
from typing import List

from src.domain.dtos.bank_item_dto import BankItemDto
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/Exporter", tags=["Exporter"])

@router.get("/{exporter_id}/banks", response_model=List[BankItemDto], response_model_by_alias=True)
async def get_exporter_banks_async(
    exporter_id: str,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    
    result = await repo.get_banks_by_exporter_id_async(exporter_id)
    return result