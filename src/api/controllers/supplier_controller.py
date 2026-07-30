from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import List

from src.domain.collections.gsupplier import GSupplier
from src.domain.dtos.supplier_dtos import SupplierListItemDto, SupplierCreateUpdateDto
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/Supplier", tags=["Supplier"])

@router.get("/", response_model=List[SupplierListItemDto], response_model_by_alias=True)
async def supplier_list_async(
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.get_supplier_list_async()

@router.post("/", response_model=GSupplier, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
async def create_supplier_async(
    dto: SupplierCreateUpdateDto,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.save_supplier_async(dto)

@router.put("/{supplier_id}", response_model=GSupplier, response_model_by_alias=True)
async def update_supplier_async(
    supplier_id: str,
    dto: SupplierCreateUpdateDto,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    updated = await repo.update_supplier_async(supplier_id, dto)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Supplier not found"
        )
    return updated

@router.delete("/{supplier_id}", response_model=GSupplier, response_model_by_alias=True)
async def delete_supplier_async(
    supplier_id: str,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    deleted = await repo.delete_supplier_async(supplier_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Supplier not found"
        )
    return deleted