import httpx
import asyncio

ISS_API_URL = "http://api.open-notify.org/iss-now.json"

async def check_connection():
    print(f"Intentando conectar a: {ISS_API_URL}")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ISS_API_URL)
            response.raise_for_status() # Lanza error para 4xx o 5xx
            data = response.json()
            print("¡Conexión exitosa!")
            print("Datos recibidos:", data)
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP (código de estado): {e.response.status_code}")
        print(f"URL: {e.request.url}")
        print(f"Respuesta: {e.response.text}")
    except httpx.RequestError as e:
        print(f"Error de Red/Petición:")
        print(f"  URL solicitada: {e.request.url}")
        print(f"  Tipo de error: {type(e)}")
        print(f"  Mensaje de error detallado: {e}")
        print(f"  Representación del error: {repr(e)}")
    except Exception as e:
        print(f"Otro error inesperado: {type(e)} - {e}")

if __name__ == "__main__":
    asyncio.run(check_connection())