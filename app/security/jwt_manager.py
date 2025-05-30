import datetime
from typing import Optional

from jose import JWTError, jwt
from app.core.config import settings # Importamos nuestra configuración (SECRET_KEY, ALGORITHM)
from app.models.token import TokenPayload # Modelo para el payload del token

def create_access_token(client_id: str) -> str:
    """
    Genera un nuevo JWT para un client_id específico.
    No se establece 'exp' para que sea "permanente" según el requisito.
    La validez real la dará su existencia en la base de datos de tokens activos.
    """
    to_encode = {"sub": client_id} # 'sub' (subject) es un claim estándar para el identificador principal
    
    # Si quisiéramos una expiración muy larga (ej. 10 años), descomentar:
    # expire_delta = datetime.timedelta(days=365 * 10)
    # expire = datetime.datetime.now(datetime.timezone.utc) + expire_delta
    # to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token_payload(token: str) -> Optional[TokenPayload]:
    """
    Decodifica un token JWT y devuelve su payload si es válido.
    No verifica la existencia en la BD de tokens aquí; eso se hace en la dependencia.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # El payload decodificado ya es un diccionario.
        # Lo pasamos a TokenPayload para validación de la estructura esperada (ej. 'sub' existe).
        return TokenPayload(**payload)
    except JWTError as e:
        print(f"Error de JWT al decodificar: {e}") # Loguear el error puede ser útil
        return None