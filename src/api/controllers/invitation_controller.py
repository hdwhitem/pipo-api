import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.domain.collections.ginvitation import GInvitation
from src.application.interfaces.imongo_repo import IMongoRepo
from src.api.config.security import verify_authorize 

router = APIRouter(prefix="/Invitation", tags=["Invitation"])

# ── DTO Auxiliar para la petición ──────────────────────
class CreateInvitationRequest(BaseModel):
    duration_hours: int = Field(default=24, ge=1, le=168, description="Duración en horas (1 a 7 días)")


# ── Endpoint ──────────────────────────────────────────

@router.post("/")
async def create_invitation_async(
    request: Request,
    payload: CreateInvitationRequest,
    user_session: dict = Depends(verify_authorize)  # Protegido: Solo administradores autorizados
):
    """
    Endpoint para que el administrador genere un nuevo código de invitación seguro de un solo uso.
    """
    repo: IMongoRepo = request.app.state.repo

    # Generamos un token alfanumérico aleatorio y sumamente seguro de 8 caracteres
    secure_code = secrets.token_urlsafe(6)[:8].upper()

    # Calculamos la fecha límite de expiración en UTC
    expiration_date = datetime.now(timezone.utc) + timedelta(hours=payload.duration_hours)

    # Instanciamos el modelo de dominio
    new_invitation = GInvitation(
        code=secure_code,
        used=False,
        expires_at=expiration_date
    )

    # Persistimos en la base de datos
    await repo.create_invitation_async(new_invitation)
    
    # Retornamos la respuesta con la estructura exacta solicitada
    return {
        "code": secure_code, 
        "expires_at": new_invitation.expires_at
    }