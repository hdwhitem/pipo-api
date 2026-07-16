# src/api/controllers/user_controller.py
from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
from fastapi import APIRouter, HTTPException, Query, Response, Request, Depends, status
from pydantic import BaseModel, Field

from src.domain.collections.gpassword_reset import GPasswordReset
from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize, RequireRole

router = APIRouter(prefix="/User", tags=["User"])

class RequestResetDto(BaseModel):
    email: str

class ResetPasswordDto(BaseModel):
    email: str
    code: str = Field(..., description="Código verificador, otorgado por el admin")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña del usuario")


@router.post("/Register")
async def register_user(
    register_dto: RegisterUserDto, 
    request: Request,
    code: str = Query(..., description="Invitation Code Required for Registration")
):
    repo: IMongoRepo = request.app.state.repo

    invitation_validation = await repo.verify_and_use_invitation_async(code)
    
    if not invitation_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=invitation_validation["message"]
        )

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
            samesite="lax" if is_development else "none",  # 'none' en Cloud para Vercel, 'lax' en Local
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


# 1. Endpoint para generar el código (Público, el usuario dice que olvidó su clave)
@router.post("/forgot-password")
async def forgot_password(
    dto: RequestResetDto, 
    request: Request,
    user_session: dict = Depends(RequireRole(allowed_roles=["Admin"]))
    ):

    repo: IMongoRepo = request.app.state.repo
    
    # Verificar si el usuario realmente existe
    user = await repo.user_collection.find_one({"UserEmail": dto.email})
    if not user:
        # Por seguridad, es mejor decir que si el correo existe se procesará, 
        # pero aquí lanzaremos un 404 para ayudar al administrador en las pruebas.
        raise HTTPException(status_code=404, detail="El correo electrónico no está registrado")
    
    # Generar un código corto y fácil de pasar de 6 dígitos alfanuméricos (ej: PR-3X8K)
    secure_code = f"PR-{secrets.token_hex(3).upper()}"
    
    # Expiración corta de 20 minutos
    expiration = datetime.now(timezone.utc) + timedelta(minutes=20)
    
    reset_obj = GPasswordReset(
        email=dto.email,
        code=secure_code,
        used=False,
        expires_at=expiration
    )
    
    await repo.create_password_reset_code_async(reset_obj)
    
    # NOTA FUTURA: Aquí irá la función 'send_email(dto.email, secure_code)'
    # Por ahora, devolvemos el código en la respuesta para que el Administrador lo tome.
    return {
        "message": "Código verificador generado con éxito. Compártelo con el usuario.",
        "code": secure_code,
        "expires_at": expiration
    }



@router.post("/reset-password")
async def reset_password(dto: ResetPasswordDto, request: Request, response: Response):
    repo: IMongoRepo = request.app.state.repo
    
    # 1. Validar y quemar el código
    validation = await repo.verify_and_use_reset_code_async(dto.email, dto.code)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["message"])
    
    # 2. Hashear la nueva contraseña
    hashed_password = bcrypt.hashpw(dto.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 3. Guardar en la base de datos
    success = await repo.update_user_password_by_email_async(dto.email, hashed_password)
    if not success:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la contraseña.")
        
    # ── EL CAMBIO DE SEGURIDAD: Expulsar la sesión actual ──
    # Si el usuario que cambia la clave era el que estaba logueado en este navegador,
    # limpiamos su cookie físicamente para obligarlo a iniciar sesión con su nueva clave.
    response.delete_cookie(key="jwt", path="/")
        
    return {
        "flag": True, 
        "message": "Su contraseña ha sido restablecida exitosamente. Por favor, inicie sesión nuevamente con sus nuevas credenciales."
    }