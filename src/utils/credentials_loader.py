"""
Cargador de credenciales desde archivos individuales en src/credentials/
Permite editar claves fácilmente en la Pi sin modificar .env
"""

import os
from pathlib import Path
from dotenv import dotenv_values

def load_credentials():
    """Carga todas las credenciales desde src/credentials/*.env"""
    credentials = {}

    # Intentar ambas rutas (relativa y absoluta)
    current_dir = Path(__file__).parent.parent
    creds_dir = current_dir / "credentials"

    # Si no existe, intentar con ruta absoluta desde /home/pi
    if not creds_dir.exists():
        creds_dir = Path("/home/pi/dosaros-data-project/src/credentials")

    if not creds_dir.exists():
        print(f"⚠️ Directorio de credenciales no encontrado: {creds_dir}")
        return credentials

    # Cargar cada archivo .env en credentials/
    for cred_file in sorted(creds_dir.glob("*.env")):
        try:
            values = dotenv_values(cred_file)
            if values:
                credentials.update(values)
                print(f"✅ Cargado: {cred_file.name} ({len(values)} variables)")
        except Exception as e:
            print(f"⚠️ Error cargando {cred_file.name}: {e}")

    return credentials

def setup_env_from_credentials():
    """Carga credenciales en os.environ - LOS ARCHIVOS TIENEN PRIORIDAD"""
    print("\n=== Cargando credenciales desde src/credentials/ ===")
    credentials = load_credentials()

    loaded_count = 0
    for key, value in credentials.items():
        # Los archivos .env SIEMPRE sobreescriben, si tienen valor válido
        if value and value != "tu_clave_aqui":
            os.environ[key] = value
            loaded_count += 1
            if "API_KEY" in key:
                print(f"  ✓ {key}: {value[:20]}...")

    print(f"✅ Total cargadas: {loaded_count} variables\n")
