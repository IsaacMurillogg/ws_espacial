# ws_prueba/app/main.py
from fastapi import FastAPI
import asyncio

from app.core.config import settings
from app.api.v1.router import api_router_v1 # Importamos la variable api_router_v1 correcta
from app.db.session import init_db
from app.services.data_poller import continuous_data_poller

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

@app.on_event("startup")
async def startup_event():
    print("Iniciando aplicación...")
    init_db() # Crea la tabla de tokens si no existe
    print("Programando la tarea de sondeo de datos en segundo plano...")
    asyncio.create_task(continuous_data_poller()) # Inicia el poller de la ISS
    print("Aplicación iniciada y lista.")

# Incluir el router principal de la API v1 con su prefijo
app.include_router(api_router_v1, prefix=settings.API_V1_STR)

@app.get("/", summary="Endpoint raíz de la API", tags=["Root"])
async def root():
    return {
        "message": f"Bienvenido a {settings.APP_TITLE}",
        "documentation_v1": f"{settings.API_V1_STR}/docs"
        }