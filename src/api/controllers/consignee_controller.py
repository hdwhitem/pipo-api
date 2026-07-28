from fastapi import APIRouter, Depends, Request, status, HTTPException
from typing import List, Optional

from src.infrastructure.persistence.documents.consignee_document import ConsigneeDocument
from src.domain.dtos.paged_result_dto import PagedResult
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/Consignee", tags=["Consignee"])

@router.get("/", response_model=PagedResult[ConsigneeDocument])
async def consignee_list_async(
    page_number: int = 1,
    page_size: int = 10,
    request: Request = None,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.consignee_list_async(page_number, page_size)

@router.get("/all", response_model=List[ConsigneeDocument])
async def get_list_consignee_async(
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    result = await repo.get_list_consignee_async()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough consignees found (requires more than 1)"
        )
    return result

@router.post("/", response_model=ConsigneeDocument, status_code=status.HTTP_201_CREATED)
async def save_consignee_async(
    consignee: ConsigneeDocument,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.save_consignee_async(consignee)

@router.put("/{consignee_id}", response_model=ConsigneeDocument)
async def update_consignee_async(
    consignee_id: str,
    consignee: ConsigneeDocument,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    updated = await repo.update_consignee_async(consignee_id, consignee)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consignee not found or invalid ID"
        )
    return updated

@router.delete("/{consignee_id}", response_model=ConsigneeDocument)
async def delete_consignee_async(
    consignee_id: str,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    deleted = await repo.delete_consignee_async(consignee_id)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consignee not found or invalid ID"
        )
    return deleted
