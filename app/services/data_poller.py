# ws_prueba/app/services/data_poller.py
import asyncio
import datetime
import random
import httpx
import json # Necesario si db_session.upsert_iss_data lo espera, aunque lo pasamos como dict

from app.core.config import settings
from app.models.unit import UnitData # Usamos para parsear la respuesta de la ISS
from app.db import session as db_session # Para guardar en la BD

ISS_UNIT_ID = "ISS-001"

async def fetch_iss_location_and_update_db():
    """
    Consulta la API de la ISS, transforma los datos y los guarda/actualiza en la BD.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.ISS_API_URL)
            response.raise_for_status()
            
            iss_api_data = response.json()

            if iss_api_data.get("message") == "success":
                position = iss_api_data.get("iss_position", {})
                timestamp_unix = iss_api_data.get("timestamp")

                if not all([position.get("latitude"), position.get("longitude"), timestamp_unix is not None]):
                    print(f"Error: Datos incompletos de la API de la ISS: {iss_api_data}")
                    return

                timestamp_dt = datetime.datetime.fromtimestamp(timestamp_unix, tz=datetime.timezone.utc)
                
                current_iss_pydantic_data = UnitData(
                    unit_id=ISS_UNIT_ID,
                    latitude=float(position["latitude"]),
                    longitude=float(position["longitude"]),
                    timestamp=timestamp_dt,
                    sensors={
                        "altitude_km": round(random.uniform(390, 430), 2),
                        "velocity_kmh": round(random.uniform(27500, 28000), 0)
                    }
                )
                
                db_session.upsert_iss_data(
                    unit_id=current_iss_pydantic_data.unit_id,
                    latitude=current_iss_pydantic_data.latitude,
                    longitude=current_iss_pydantic_data.longitude,
                    api_timestamp=current_iss_pydantic_data.timestamp,
                    sensors=current_iss_pydantic_data.sensors
                )
                # print(f"[{datetime.datetime.now()}] Datos de la ISS actualizados en la BD para {ISS_UNIT_ID}")
            else:
                print(f"Error: La API de la ISS no reportó éxito. Mensaje: {iss_api_data.get('message')}")

    except httpx.HTTPStatusError as e:
        print(f"Error HTTP al consultar la API de la ISS: {e.response.status_code} - {e.request.url}")
    except httpx.RequestError as e:
        print(f"Error de red al consultar la API de la ISS:")
        print(f"  URL solicitada: {e.request.url}")
        print(f"  Tipo de error: {type(e)}")
        print(f"  Mensaje de error detallado: {e}")
        print(f"  Representación del error: {repr(e)}")
    except Exception as e:
        print(f"Error inesperado ({type(e).__name__}) al procesar datos de la ISS: {e}")


async def continuous_data_poller(): # <--- ¡AQUÍ ESTÁ LA FUNCIÓN!
    """
    Tarea en segundo plano que llama a fetch_iss_location_and_update_db()
    periódicamente según el intervalo definido en la configuración.
    """
    print(f"[{datetime.datetime.now()}] Iniciando sondeo continuo de datos de la ISS (intervalo: {settings.POLLING_INTERVAL_SECONDS}s) para BD...")
    while True:
        print(f"[{datetime.datetime.now()}] Poller: Intentando obtener y actualizar datos de la ISS en BD...")
        await fetch_iss_location_and_update_db()
        await asyncio.sleep(settings.POLLING_INTERVAL_SECONDS)