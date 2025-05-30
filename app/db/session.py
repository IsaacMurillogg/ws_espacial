import sqlite3
import os
import json # Para convertir el diccionario de sensores a string y viceversa
import datetime # Para manejar timestamps
from typing import Optional, List, Dict, Any

from app.core.config import settings

os.makedirs(settings.SQLITE_INSTANCE_DIR, exist_ok=True)

# LA LÍNEA "router = APIRouter()" NO DEBE ESTAR AQUÍ

def get_db_connection():
    conn = sqlite3.connect(settings.SQLITE_DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabla de Tokens (existente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Nueva tabla para los datos de la ISS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS iss_data (
            unit_id TEXT PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            api_timestamp TEXT NOT NULL, 
            sensors_json TEXT,         
            last_updated_at_service TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"Base de datos inicializada/actualizada en {settings.SQLITE_DATABASE_URL}")

def store_token(client_id: str, token: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO active_tokens (client_id, token) VALUES (?, ?)",
            (client_id, token)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Error: El token para el cliente {client_id} podría ya existir.")
        conn.rollback()
        return False
    finally:
        conn.close()

def revoke_token(token: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_tokens WHERE token = ?", (token,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted

def is_token_active(token: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, created_at FROM active_tokens WHERE token = ?", (token,))
    token_data = cursor.fetchone()
    conn.close()
    if token_data:
        return {"client_id": token_data["client_id"], "created_at": token_data["created_at"]}
    return None

def get_active_tokens_for_admin() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, token, created_at FROM active_tokens ORDER BY created_at DESC")
    tokens_raw = cursor.fetchall()
    conn.close()
    return [
        {"client_id": row["client_id"], "token": row["token"], "created_at": row["created_at"]}
        for row in tokens_raw
    ]

def upsert_iss_data(unit_id: str, latitude: float, longitude: float, api_timestamp: datetime.datetime, sensors: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    api_timestamp_str = api_timestamp.isoformat()
    sensors_str = json.dumps(sensors)
    cursor.execute("""
        INSERT OR REPLACE INTO iss_data (unit_id, latitude, longitude, api_timestamp, sensors_json, last_updated_at_service)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (unit_id, latitude, longitude, api_timestamp_str, sensors_str))
    conn.commit()
    conn.close()

def get_iss_data_by_id(unit_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT unit_id, latitude, longitude, api_timestamp, sensors_json FROM iss_data WHERE unit_id = ?", (unit_id,)) # Quité last_updated_at_service para simplificar
    data_row = cursor.fetchone()
    conn.close()
    if data_row:
        sensors = json.loads(data_row["sensors_json"]) if data_row["sensors_json"] else {}
        return {
            "unit_id": data_row["unit_id"],
            "latitude": data_row["latitude"],
            "longitude": data_row["longitude"],
            "timestamp": data_row["api_timestamp"],
            "sensors": sensors,
        }
    return None

def get_all_iss_data_from_db() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT unit_id, latitude, longitude, api_timestamp, sensors_json FROM iss_data")
    data_rows = cursor.fetchall()
    conn.close()
    results = []
    for row in data_rows:
        sensors = json.loads(row["sensors_json"]) if row["sensors_json"] else {}
        results.append({
            "unit_id": row["unit_id"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "timestamp": row["api_timestamp"],
            "sensors": sensors
        })
    return results