# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    APP_TITLE: str = "Empresa 1 API Service"
    APP_DESCRIPTION: str = "API para proveer datos de unidades en tiempo real a clientes."
    API_V1_STR: str = "/api/v1"

    # Configuración JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # API Externa
    ISS_API_URL: str = "http://api.open-notify.org/iss-now.json"
    POLLING_INTERVAL_SECONDS: int = 10 # IMPORTANTE: Debe ser int y un valor por defecto

    # Base de datos de Tokens
    SQLITE_DATABASE_URL: str = "instance/tokens.db"
    SQLITE_INSTANCE_DIR: str = "instance"

    # Carga la configuración desde un archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# YA NO NECESITAMOS LAS LÍNEAS DE print() PARA DEPURACIÓN AQUÍ