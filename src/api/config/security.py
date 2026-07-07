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
        is_development = repo.jwt_audience in ["localhost", "127.0.0.1"]

        decoded = jwt.decode(
            token, 
            repo.jwt_key, 
            issuer=repo.jwt_issuer, 
            algorithms=["HS256"],
            # Si es desarrollo local, ignora el Audience. Si es producción, lo obliga a coincidir.
            options={"verify_aud": not is_development}, 
            audience=repo.jwt_audience # Se usa si verify_aud es True
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