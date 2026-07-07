# src/api/controllers/user_controller.py
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Response, Request, Depends

from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize

router = APIRouter(prefix="/User", tags=["User"])


@router.post("/Register")
async def register_user(register_dto: RegisterUserDto, request: Request):
    repo: IMongoRepo = request.app.state.repo
    result = await repo.register_user_async(register_dto)
    return result


@router.post("/login")
async def log_user_in(login_dto: LoginDto, response: Response, request: Request):
    repo: IMongoRepo = request.app.state.repo
    result = await repo.login_user_async(login_dto)
    
    if result["flag"]:
        # Inyección segura de la cookie HttpOnly
        is_development = repo.jwt_audience in ["localhost", "127.0.0.1"]
        response.set_cookie(
            key="jwt",
            value=result["token"],
            httponly=True,
            secure=not is_development,
            samesite="lax",
            max_age=3600,
            path="/"
        )
        min_exp = repo.duration
        expiration_time = (datetime.now(timezone.utc) + timedelta(minutes=min_exp)).isoformat()
        
        return {
            "flag": result["flag"],
            "message": result["message"],
            "expiresAt": expiration_time,
            "name": result["name"],
            "email": result["email"]
        }
        
    return result


@router.get("/verify")
def verify_session(user_session: dict = Depends(verify_authorize)):
    # Si pasa el Depends, significa que el token es válido.
    return {"flag": True}


@router.post("/logout")
def logout_user(response: Response):
    # Eliminación física de la cookie en el navegador
    response.delete_cookie(key="jwt", path="/")
    return {"message": "Sesión cerrada correctamente"}