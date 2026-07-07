import jwt
from fastapi import Request, HTTPException, status
from src.application.interfaces.imongo_repo import IMongoRepo

def verify_authorize(request: Request) -> dict:
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
        raise HTTPException(status_code=401, detail=f"Error: El Issuer no coincide.")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail=f"Error: El Audience no coincide.")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Error: La firma del token no coincide (JWT_KEY incorrecta o diferente entre firmas).")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Error interno de JWT")