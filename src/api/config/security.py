import jwt
from fastapi import Request, HTTPException, status
from src.application.interfaces.imongo_repo import IMongoRepo

def verify_authorize(request: Request) -> dict:
    """
    Validación de autenticación básica.
    Verifica que el token sea válido, firma, audiencias y emisor.
    """
    repo: IMongoRepo = request.app.state.repo
    
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("jwt")
        
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado (Falta Cookie/Token)")
        
    try:
        base_audience = repo.jwt_audience.strip() if repo.jwt_audience else "localhost"
        is_development = repo.jwt_audience in ["localhost", "127.0.0.1"]

        allowed_audiences = [
            base_audience,
            base_audience.rstrip("/"),
            base_audience + "/" if not base_audience.endswith("/") else base_audience
        ]

        decoded = jwt.decode(
            token, 
            repo.jwt_key, 
            issuer=repo.jwt_issuer, 
            algorithms=["HS256"],
            options={"verify_aud": not is_development}, 
            audience=allowed_audiences
        )
        return decoded
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Error: El token realmente está expirado en el tiempo.")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Error: El Issuer no coincide.")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Error: El Audience no coincide.")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Error: La firma del token no coincide (JWT_KEY incorrecta o diferente entre firmas).")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Error interno de JWT")


class RequireRole:
    """
    Clase de Autorización por Roles al estilo .NET.
    Reutiliza internamente tu 'verify_authorize' para validar el token 
    y luego filtra por los roles permitidos.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request) -> dict:
        # 1. Primero delegamos la validación del token a tu función de siempre
        decoded_token = verify_authorize(request)
        
        # 2. Extraemos el rol usando el Claim estándar de .NET
        role_claim = "http://schemas.microsoft.com/ws/2008/06/identity/claims/role"
        user_role = decoded_token.get(role_claim)
        
        # 3. Comprobamos si el rol del usuario está autorizado para este endpoint
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. No tiene los permisos de rol requeridos para esta acción."
            )
            
        return decoded_token