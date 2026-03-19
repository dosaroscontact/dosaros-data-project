import sqlite3
import logging
from pathlib import Path

DB_PATH = Path("/mnt/nba_data/dosaros_local.db")

def get_db_connection():
    """Crea una conexión a la base de datos local."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Permite acceder a las columnas por nombre
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error conectando a la base de datos: {e}")
        raise

def setup_logging():
    """Configuración básica de logs."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )