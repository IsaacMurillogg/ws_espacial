# ws_prueba/app/main.py
from fastapi import FastAPI, Request # Request en mayúscula aquí
import asyncio
import datetime # Para el año en el footer

from app.core.config import settings
from app.api.v1.router import api_router_v1
from app.db.session import init_db
from app.services.data_poller import continuous_data_poller
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ÚNICA Y CORRECTA INICIALIZACIÓN DE TEMPLATES
# Debe estar antes de la definición de 'app = FastAPI(...)'
templates = Jinja2Templates(directory="app/templates")

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
    init_db()
    print("Programando la tarea de sondeo de datos en segundo plano...")
    asyncio.create_task(continuous_data_poller())
    print("Aplicación iniciada y lista.")

app.include_router(api_router_v1, prefix=settings.API_V1_STR)

# ELIMINA CUALQUIER OTRA LÍNEA 'templates = Jinja2Templates(...)' QUE PUDIERA ESTAR AQUÍ ABAJO

@app.get("/", response_class=HTMLResponse, summary="Página de Inicio", tags=["Root"])
async def root(request: Request): # 'request' como nombre del parámetro
    """
    Muestra la página de inicio HTML con información sobre la API.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, # Pasa el objeto request
            "app_title": settings.APP_TITLE,
            "app_description": settings.APP_DESCRIPTION,
            "docs_url": app.docs_url,
            "current_year": datetime.datetime.now().year
        }
    )