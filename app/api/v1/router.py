# ws_prueba/app/api/v1/router.py
from fastapi import APIRouter

# Importamos los módulos que contienen nuestros routers específicos
from app.api.v1.endpoints import admin_tokens
from app.api.v1.endpoints import client_data

# Creamos la instancia principal del router para la API v1
api_router_v1 = APIRouter()

# Incluimos el router de admin_tokens, con un prefijo para sus rutas
api_router_v1.include_router(
    admin_tokens.router, # El objeto 'router' definido en admin_tokens.py
    prefix="/admin",     # Todas las rutas en admin_tokens.router comenzarán con /admin
    tags=["Admin Tokens"] # Etiqueta para la documentación de Swagger UI
)

# Incluimos el router de client_data, con un prefijo para sus rutas
api_router_v1.include_router(
    client_data.router,  # El objeto 'router' definido en client_data.py
    prefix="/client",    # Todas las rutas en client_data.router comenzarán con /client
    tags=["Client Data"] # Etiqueta para la documentación de Swagger UI
)