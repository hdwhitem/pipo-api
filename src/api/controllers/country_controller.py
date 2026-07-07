from fastapi import APIRouter, Depends, Request
from typing import List

from src.domain.collections.gcountry import Gcountry
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize 

router = APIRouter(prefix="/Country", tags=["Country"])

@router.get("/", response_model=List[Gcountry])
async def country_list_async(
    request: Request, 
    user_session: dict = Depends(verify_authorize)
):
    repo: IMongoRepo = request.app.state.repo
    
    result = await repo.get_country_list_async()
    return result