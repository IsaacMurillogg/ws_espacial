from pydantic import BaseModel, Field
from typing import Optional
import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    client_id: str

class TokenPayload(BaseModel):
    # El 'sub' (subject) del JWT contendrá el client_id
    sub: Optional[str] = None

class ClientInfoInput(BaseModel):
    client_id: str = Field(..., example="empresa_2_cliente_alfa")

class TokenRevokeInput(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...") # Ejemplo de token

class ActiveTokenAdminView(BaseModel):
    client_id: str
    token: str
    created_at: datetime.datetime