# ws_prueba/app/api/v1/deps.py
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.session import is_token_active  # Función de session.py
from app.security import jwt_manager       # Módulo jwt_manager.py
from app.models.token import TokenPayload    # Modelo Pydantic
from app.core.config import settings       # Configuración de la app

# El tokenUrl es informativo para la documentación de Swagger / OpenAPI.
# Indica dónde se podrían obtener tokens (aunque en nuestro caso es administrativo).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/admin/tokens/how_to_get_token_docs")

async def get_current_active_client(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Dependencia para obtener el cliente actual basado en un token JWT válido y activo.
    Pasos:
    1. Decodifica el token JWT para obtener el payload (verifica firma y estructura básica).
    2. Verifica si el token completo existe y está activo en nuestra base de datos de tokens.
    3. Compara el client_id del payload con el almacenado en la BD para ese token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decodificar el token y obtener el payload
    payload: Optional[TokenPayload] = jwt_manager.verify_token_payload(token)
    
    # Verificar que el payload no sea None y que contenga el 'sub' (client_id)
    if payload is None or payload.sub is None:
        raise credentials_exception

    # 2. Verificar si el token está en nuestra base de datos de tokens activos
    active_token_data = is_token_active(token=token) # Espera Optional[dict] o None
    if not active_token_data:
        # Si el token no está en nuestra BD, se considera inválido o fue revocado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o revocado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verificar consistencia entre el client_id del payload y el de la BD asociada al token
    if active_token_data.get("client_id") != payload.sub:
        # Esto sería un estado inconsistente, no debería ocurrir si la lógica es correcta.
        print(f"ALERTA DE SEGURIDAD o INCONSISTENCIA: Discrepancia de client_id para el token. "
              f"Payload sub: '{payload.sub}', DB client_id: '{active_token_data.get('client_id')}'")
        raise credentials_exception
        
    # Si todas las validaciones pasan, el payload (que es de tipo TokenPayload) es devuelto.
    # TokenPayload.sub contiene el client_id.
    return payload