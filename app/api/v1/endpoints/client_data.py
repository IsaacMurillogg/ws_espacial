# ws_espacial/app/api/v1/endpoints/client_data.py
from fastapi import APIRouter, HTTPException, status # Quitamos Depends
from typing import List

# Modelos Pydantic para la respuesta
from app.models.unit import UnitDataPublic
# Ya no necesitamos TokenPayload ni get_current_active_client aquí

# Módulo de sesión de base de datos para interactuar con la BD
from app.db import session as db_session

# El unit_id que estamos buscando para el endpoint específico de la ISS
ISS_UNIT_ID = "ISS-001"

router = APIRouter()

@router.get(
    "/units/data",
    response_model=UnitDataPublic,
    summary="Obtiene los últimos datos públicos de la unidad ISS",
    description="Devuelve la información más reciente de telemetría de la Estación Espacial Internacional (ISS) almacenada en el sistema. Este endpoint es de acceso público."
)
async def get_public_iss_unit_data(): # Eliminamos current_client y Depends
    """
    Endpoint público para obtener los datos más recientes de la ISS.
    """
    iss_data_from_db = db_session.get_iss_data_by_id(unit_id=ISS_UNIT_ID)

    if not iss_data_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datos para la unidad '{ISS_UNIT_ID}' no encontrados. El poller podría no haber corrido aún o no hay datos."
        )

    try:
        response_data = UnitDataPublic(
            unit_id=iss_data_from_db["unit_id"],
            latitude=iss_data_from_db["latitude"],
            longitude=iss_data_from_db["longitude"],
            timestamp_iso=iss_data_from_db["timestamp"],
            sensors=iss_data_from_db["sensors"]
        )
        return response_data
    except Exception as e:
        print(f"Error al convertir datos de la BD a UnitDataPublic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar los datos de la unidad."
        )

@router.get(
    "/units",
    response_model=List[UnitDataPublic],
    summary="Obtiene datos públicos de todas las unidades disponibles",
    description="Devuelve una lista con la información de telemetría más reciente de todas las unidades monitoreadas almacenadas en el sistema. Este endpoint es de acceso público."
)
async def get_public_all_units_data(): # Eliminamos current_client y Depends
    """
    Endpoint público para obtener los datos más recientes de todas las unidades.
    """
    all_data_from_db = db_session.get_all_iss_data_from_db()

    if not all_data_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron datos de unidades. El poller podría no haber corrido aún o no hay datos."
        )
    
    response_list = []
    try:
        for data_item in all_data_from_db:
            response_list.append(UnitDataPublic(
                unit_id=data_item["unit_id"],
                latitude=data_item["latitude"],
                longitude=data_item["longitude"],
                timestamp_iso=data_item["timestamp"],
                sensors=data_item["sensors"]
            ))
        return response_list
    except Exception as e:
        print(f"Error al convertir lista de datos de la BD a List[UnitDataPublic]: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la lista de datos de unidades."
        )
