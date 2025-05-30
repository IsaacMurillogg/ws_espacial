from pydantic import BaseModel, Field
from typing import Dict, Any
import datetime

class UnitData(BaseModel):
    unit_id: str = Field(..., example="ISS-001")
    latitude: float
    longitude: float
    timestamp: datetime.datetime # Almacenaremos como objeto datetime
    sensors: Dict[str, Any] = Field(default_factory=dict)

class UnitDataPublic(BaseModel): # Lo que expondremos en la API
    unit_id: str
    latitude: float
    longitude: float
    # El timestamp se convertirá a string ISO para la respuesta JSON
    timestamp_iso: str = Field(..., alias="timestamp")
    sensors: Dict[str, Any]

    # Configuración para permitir alias en la serialización
    model_config = {
        "populate_by_name": True # Permite usar 'timestamp' para el campo 'timestamp_iso' durante la creación del modelo
    }