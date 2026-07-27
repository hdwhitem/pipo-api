from fastapi import APIRouter, Depends, Request, status, HTTPException
from typing import List

from src.infrastructure.persistence.documents.colour_document import ColourDocument
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/Colour", tags=["Colour"])

@router.get("/", response_model=List[ColourDocument])
async def colour_list_async(
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.get_colour_list_async()

@router.post("/", response_model=ColourDocument, status_code=status.HTTP_201_CREATED)
async def save_colour_async(
    colour: ColourDocument,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    return await repo.save_colour_async(colour)

@router.delete("/{colour_id}", response_model=ColourDocument)
async def delete_colour_async(
    colour_id: str,
    request: Request,
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    deleted = await repo.delete_colour_async(colour_id)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colour not found or invalid ID"
        )
    return deleted
