import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargamos las variables del archivo .env
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Crea y devuelve una instancia del cliente de Supabase."""
    if not url or not key:
        raise ValueError("Faltan las credenciales de Supabase en el archivo .env")
    return create_client(url, key)

# Prueba rápida de conexión
if __name__ == "__main__":
    try:
        client = get_supabase_client()
        print("Conexión exitosa con Proyecto Dos Aros en Supabase")
    except Exception as e:
        print(f"Error al conectar: {e}")