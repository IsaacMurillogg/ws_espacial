from typing import Dict, Optional, List
from app.models.unit import UnitData # Nuestro modelo Pydantic para los datos de unidad
import threading # Para un bloqueo simple si se accede concurrentemente (buena práctica)

class InMemoryCache:
    def __init__(self):
        self._cache: Dict[str, UnitData] = {}
        self._lock = threading.Lock() # Para la seguridad en hilos (aunque FastAPI con asyncio es de un solo hilo por worker)

    def get(self, unit_id: str) -> Optional[UnitData]:
        with self._lock:
            return self._cache.get(unit_id)

    def set(self, unit_id: str, data: UnitData):
        with self._lock:
            self._cache[unit_id] = data
            # print(f"Cache updated for {unit_id}: {data.latitude}, {data.longitude}") # Para depuración

    def get_all(self) -> List[UnitData]:
        with self._lock:
            return list(self._cache.values())

    def is_empty(self) -> bool:
        with self._lock:
            return not bool(self._cache)

# Instancia global del caché (Singleton simple para este demo)
# En una aplicación más grande, esto podría gestionarse con inyección de dependencias.
unit_data_cache = InMemoryCache()