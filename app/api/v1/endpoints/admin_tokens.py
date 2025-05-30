# ws_prueba/app/api/v1/endpoints/admin_tokens.py
from fastapi import APIRouter, HTTPException, Body, status, Depends
from typing import List

from app.security import jwt_manager
from app.db import session as db_session
from app.models.token import Token, ClientInfoInput, TokenRevokeInput, ActiveTokenAdminView

router = APIRouter() # Correcto

@router.post(
    "/tokens/generate",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Genera un nuevo token JWT para un cliente",
)
async def generate_token_for_client(client_info: ClientInfoInput = Body(...)):
    client_id = client_info.client_id
    access_token = jwt_manager.create_access_token(client_id=client_id)

    if not db_session.store_token(client_id=client_id, token=access_token):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo almacenar el token."
        )
    return Token(access_token=access_token, token_type="bearer", client_id=client_id)

@router.post(
    "/tokens/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoca (elimina) un token JWT existente",
)
async def revoke_token(token_input: TokenRevokeInput = Body(...)):
    rows_deleted = db_session.revoke_token(token=token_input.token)
    if rows_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado o ya fue revocado."
        )
    return {"message": "Token revocado exitosamente."}

@router.get(
    "/tokens/active",
    response_model=List[ActiveTokenAdminView],
    summary="Lista todos los tokens JWT activos (para propósitos de demo/admin)",
)
async def list_active_tokens():
    active_tokens_raw = db_session.get_active_tokens_for_admin()
    return [
        ActiveTokenAdminView(
            client_id=row["client_id"],
            token=row["token"],
            created_at=row["created_at"]
        ) for row in active_tokens_raw
    ]

@router.get("/tokens/how_to_get_token_docs", include_in_schema=False)
async def token_docs():
    return {
        "message": "Los tokens se generan administrativamente a través del endpoint POST /api/v1/admin/tokens/generate."
    }