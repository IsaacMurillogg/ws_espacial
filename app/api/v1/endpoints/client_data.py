# ws_espacial/app/api/v1/endpoints/client_data.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# Modelos Pydantic para la respuesta y el payload del token
from app.models.unit import UnitDataPublic
from app.models.token import TokenPayload

# Dependencia para la autenticación y obtención del cliente actual
from app.api.v1.deps import get_current_active_client

# Módulo de sesión de base de datos para interactuar con la BD
# Asegúrate de que app.db.session contiene las funciones como get_iss_data_by_id, etc.
from app.db import session as db_session

# El unit_id que estamos buscando para el endpoint específico de la ISS
ISS_UNIT_ID = "ISS-001"

router = APIRouter()

@router.get(
    "/units/data",
    response_model=UnitDataPublic,
    summary="Obtiene los últimos datos de la unidad ISS",
    description="Devuelve la información más reciente de telemetría de la Estación Espacial Internacional (ISS) almacenada en el sistema."
)
async def get_iss_unit_data(
    current_client: TokenPayload = Depends(get_current_active_client) # Protege el endpoint
):
    """
    Endpoint para que los clientes autenticados obtengan los datos más recientes de la ISS.
    """
    # Obtener datos de la ISS desde la base de datos
    # Esta función debe existir en app.db.session
    iss_data_from_db = db_session.get_iss_data_by_id(unit_id=ISS_UNIT_ID)

    if not iss_data_from_db:
        # Si no se encuentran datos, devuelve un error 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datos para la unidad '{ISS_UNIT_ID}' no encontrados. El poller podría no haber corrido aún o no hay datos."
        )

    # Construye la respuesta usando el modelo Pydantic UnitDataPublic
    # El modelo UnitDataPublic espera 'timestamp_iso' como alias de 'timestamp'
    # y get_iss_data_by_id devuelve 'timestamp' como string ISO,
    # por lo que el mapeo debería ser directo.
    try:
        response_data = UnitDataPublic(
            unit_id=iss_data_from_db["unit_id"],
            latitude=iss_data_from_db["latitude"],
            longitude=iss_data_from_db["longitude"],
            timestamp_iso=iss_data_from_db["timestamp"], # FastAPI usará el alias 'timestamp'
            sensors=iss_data_from_db["sensors"]
        )
        return response_data
    except Exception as e:
        # Captura cualquier error durante la creación del modelo de respuesta
        print(f"Error al convertir datos de la BD a UnitDataPublic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar los datos de la unidad."
        )

@router.get(
    "/units",
    response_model=List[UnitDataPublic],
    summary="Obtiene datos de todas las unidades disponibles",
    description="Devuelve una lista con la información de telemetría más reciente de todas las unidades monitoreadas almacenadas en el sistema."
)
async def get_all_units_data(
    current_client: TokenPayload = Depends(get_current_active_client) # Protege el endpoint
):
    """
    Endpoint para que los clientes autenticados obtengan los datos más recientes de todas las unidades.
    """
    # Obtener todos los datos de unidades desde la base de datos
    # Esta función debe existir en app.db.session
    all_data_from_db = db_session.get_all_iss_data_from_db()

    if not all_data_from_db:
        # Si no se encuentran datos, devuelve un error 404
        # Podrías devolver una lista vacía si eso es más apropiado para tu caso de uso: return []
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron datos de unidades. El poller podría no haber corrido aún o no hay datos."
        )
    
    response_list = []
    try:
        for data_item in all_data_from_db:
            # Convierte cada item del diccionario de la BD a un modelo UnitDataPublic
            response_list.append(UnitDataPublic(
                unit_id=data_item["unit_id"],
                latitude=data_item["latitude"],
                longitude=data_item["longitude"],
                timestamp_iso=data_item["timestamp"], # FastAPI usará el alias 'timestamp'
                sensors=data_item["sensors"]
            ))
        return response_list
    except Exception as e:
        # Captura cualquier error durante la creación de la lista de modelos de respuesta
        print(f"Error al convertir lista de datos de la BD a List[UnitDataPublic]: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la lista de datos de unidades."
        )
