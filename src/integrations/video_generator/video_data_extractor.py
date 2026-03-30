"""
video_data_extractor.py — Extractor de datos para generador de videos
Mapea apodos → nombres reales, valida en BD, devuelve datos precisos.

Uso:
    extractor = VideoDataExtractor()
    data = extractor.extraer_jugador(instruccion="Top 3 puntos de Shai")
    # → {'nombre': 'Gilgeous-Alexander', 'liga': 'nba', 'stat': 'PTS', ...}
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# Cargar mapeo de apodos desde assets/player_aliases.json
ALIASES_PATH = Path(__file__).parents[2] / "assets" / "player_aliases.json"
try:
    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        PLAYER_ALIASES = json.load(f)
except FileNotFoundError:
    print(f"⚠️  {ALIASES_PATH} no encontrado. Usando apodos básicos.")
    PLAYER_ALIASES = {
        "shai": "Gilgeous-Alexander",
        "luka": "Doncic",
        "jokic": "Jokic",
        "giannis": "Antetokounmpo",
        "lebron": "James",
    }

# Equipos NBA (para validar)
NBA_TEAMS = {
    "LAL": "Los Angeles Lakers", "LAC": "Los Angeles Clippers",
    "GSW": "Golden State Warriors", "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets", "PHX": "Phoenix Suns",
    "MIA": "Miami Heat", "BOS": "Boston Celtics",
    "NYK": "New York Knicks", "MIL": "Milwaukee Bucks",
    "CHI": "Chicago Bulls", "TOR": "Toronto Raptors",
    "CLE": "Cleveland Cavaliers", "ATL": "Atlanta Hawks",
    "WAS": "Washington Wizards", "PHI": "Philadelphia 76ers",
    "BRK": "Brooklyn Nets", "ORL": "Orlando Magic",
    "IND": "Indiana Pacers", "CHA": "Charlotte Hornets",
    "NOP": "New Orleans Pelicans", "MEM": "Memphis Grizzlies",
    "DET": "Detroit Pistons", "MIN": "Minnesota Timberwolves",
    "UTA": "Utah Jazz", "HOU": "Houston Rockets",
    "POR": "Portland Trail Blazers", "SAS": "San Antonio Spurs",
    "SAC": "Sacramento Kings", "OKC": "Oklahoma City Thunder",
}


class VideoDataExtractor:
    """Extrae y valida datos precisos de BD para generación de videos."""

    def __init__(self):
        self.db = DB_PATH
        self._validar_db()

    def _validar_db(self):
        """Verifica que la BD existe y tiene las tablas necesarias."""
        if not os.path.exists(self.db):
            raise FileNotFoundError(f"BD no encontrada: {self.db}")
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('nba_players_games', 'nba_games')"
            )
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            if not tables:
                raise ValueError("Tablas NBA no encontradas en BD")
        except Exception as e:
            raise ValueError(f"Error validando BD: {e}")

    # ──────────────────────────────────────────────
    # Extracción de parámetros
    # ──────────────────────────────────────────────

    def mapear_nombre(self, nombre: str) -> str:
        """Mapea apodo a nombre real. Ej: 'Shai' → 'Gilgeous-Alexander'."""
        nombre_lower = nombre.lower().strip()
        
        # Búsqueda exacta en aliases
        if nombre_lower in PLAYER_ALIASES:
            return PLAYER_ALIASES[nombre_lower]
        
        # Búsqueda por palabra clave (ej: "shai" en "shai gilgeous")
        for alias, real_name in PLAYER_ALIASES.items():
            if alias in nombre_lower:
                return real_name
        
        # Si no encuentra mapeo, devuelve el nombre original (capitalizado)
        return nombre.title()

    def validar_jugador_en_bd(self, nombre_mapped: str, liga: str = "nba") -> Optional[Dict]:
        """
        Verifica que el jugador existe en BD y devuelve su información.
        
        Returns:
            {'nombre': 'Gilgeous-Alexander', 'eq': ['OKC'], 'temporadas': [2024, 2025]}
            o None si no existe.
        """
        if liga != "nba":
            return None  # Por ahora solo NBA
        
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.execute(
                """
                SELECT DISTINCT PLAYER_NAME, TEAM_ABBREVIATION, SEASON_ID
                FROM nba_players_games
                WHERE PLAYER_NAME LIKE ?
                ORDER BY SEASON_ID DESC
                """,
                (f"%{nombre_mapped}%",),
            )
            filas = cursor.fetchall()
            conn.close()
            
            if not filas:
                return None
            
            # Agrupar por nombre exacto, equipos y temporadas
            nombre_exact = filas[0][0]
            equipos = sorted(set(f[1] for f in filas))
            temporadas = sorted(set(int(f[2]) for f in filas))
            
            return {
                "nombre": nombre_exact,
                "equipos": equipos,
                "temporadas": temporadas,
            }
        except Exception as e:
            print(f"  Error validando jugador '{nombre_mapped}': {e}")
            return None

    def extraer_jugador(self, instruccion: str) -> Optional[Dict]:
        """
        Extrae nombre de jugador desde instrucción, mapea apodo, valida en BD.
        
        Args:
            instruccion: "Top 3 puntos de Shai en los últimos 20 partidos"
        
        Returns:
            {
                'tipo': 'jugador',
                'nombre_original': 'Shai',
                'nombre_mapped': 'Gilgeous-Alexander',
                'equipos': ['OKC'],
                'stat': 'PTS',
                'periodo': 'ultimos_20_partidos'
            }
            o None si no identifica jugador.
        """
        instruccion_lower = instruccion.lower()
        
        # Patrones para extraer nombre (mejorables)
        patron_de = r'de\s+(\w+)'
        patron_puntos = r'(puntos|points|pts)\s+de\s+(\w+)'
        
        nombre_candidato = None
        
        # Intenta encontrar "de <nombre>"
        match = re.search(patron_de, instruccion_lower)
        if match:
            nombre_candidato = match.group(1)
        
        # Intenta encontrar "puntos de <nombre>"
        match = re.search(patron_puntos, instruccion_lower)
        if match:
            nombre_candidato = match.group(2)
        
        if not nombre_candidato:
            return None
        
        # Mapear apodo
        nombre_mapped = self.mapear_nombre(nombre_candidato)
        
        # Validar en BD
        validacion = self.validar_jugador_en_bd(nombre_mapped)
        if not validacion:
            print(f"  ⚠️  Jugador '{nombre_mapped}' no encontrado en BD")
            return None
        
        # Extraer estadística
        stat = "PTS"  # Default
        for stat_name in ["AST", "REB", "STL", "BLK", "FG3M"]:
            if stat_name.lower() in instruccion_lower:
                stat = stat_name
                break
        
        return {
            "tipo": "jugador",
            "nombre_original": nombre_candidato,
            "nombre_mapped": validacion["nombre"],
            "equipos": validacion["equipos"],
            "temporadas": validacion["temporadas"],
            "stat": stat,
            "instruccion_original": instruccion,
        }

    def extraer_equipo(self, instruccion: str) -> Optional[Dict]:
        """
        Extrae equipo desde instrucción.
        Ej: "Top 5 anotadores de Lakers" → {'equipo': 'LAL', 'stat': 'PTS'}
        """
        instruccion_lower = instruccion.lower()
        
        for code, nombre_largo in NBA_TEAMS.items():
            # Buscar por código (LAL) o nombre (Lakers)
            if code.lower() in instruccion_lower or nombre_largo.lower() in instruccion_lower:
                stat = "PTS"
                if "asistencias" in instruccion_lower or "ast" in instruccion_lower:
                    stat = "AST"
                elif "rebotes" in instruccion_lower:
                    stat = "REB"
                
                return {
                    "tipo": "equipo",
                    "equipo": code,
                    "equipo_nombre": nombre_largo,
                    "stat": stat,
                    "instruccion_original": instruccion,
                }
        
        return None

    # ──────────────────────────────────────────────
    # Consultas SQL
    # ──────────────────────────────────────────────

    def datos_jugador_ultimos_partidos(
        self, nombre_mapped: str, stat: str = "PTS", num_partidos: int = 20
    ) -> Dict:
        """
        Obtiene últimos N partidos de un jugador con estadística.
        
        Returns:
            {
                'registros': [...],
                'promedio': 25.5,
                'max': 35,
                'min': 15,
                'count': 20
            }
        """
        try:
            conn = sqlite3.connect(self.db)
            sql = f"""
                SELECT PLAYER_NAME, TEAM_ABBREVIATION, GAME_DATE, {stat}, MIN
                FROM nba_players_games
                WHERE PLAYER_NAME = ?
                ORDER BY GAME_DATE DESC
                LIMIT ?
            """
            cursor = conn.execute(sql, (nombre_mapped, num_partidos))
            cols = [d[0] for d in cursor.description]
            filas = cursor.fetchall()
            conn.close()
            
            registros = [dict(zip(cols, f)) for f in filas]
            valores = [r[stat] for r in registros if r[stat] is not None]
            
            return {
                "registros": registros,
                "promedio": round(sum(valores) / len(valores), 1) if valores else 0,
                "maximo": max(valores) if valores else 0,
                "minimo": min(valores) if valores else 0,
                "count": len(registros),
                "stat": stat,
            }
        except Exception as e:
            print(f"  Error consultando datos de {nombre_mapped}: {e}")
            return {"registros": [], "count": 0, "error": str(e)}

    def datos_top_jugadores(
        self, stat: str = "PTS", liga: str = "nba", dias: int = 7, limit: int = 5
    ) -> Dict:
        """
        Top N jugadores por estadística en los últimos D días.
        
        Returns:
            {
                'registros': [
                    {'PLAYER_NAME': 'Gilgeous-Alexander', 'TEAM_ABBREVIATION': 'OKC', 'valor': 28.5},
                    ...
                ]
            }
        """
        try:
            conn = sqlite3.connect(self.db)
            sql = f"""
                SELECT PLAYER_NAME, TEAM_ABBREVIATION,
                       ROUND(AVG({stat}), 1) AS valor,
                       COUNT(*) as games
                FROM nba_players_games
                WHERE GAME_DATE >= date('now', '-{dias} days')
                  AND {stat} IS NOT NULL
                  AND MIN > 0
                GROUP BY PLAYER_NAME, TEAM_ABBREVIATION
                HAVING games >= 2
                ORDER BY valor DESC
                LIMIT ?
            """
            cursor = conn.execute(sql, (limit,))
            cols = [d[0] for d in cursor.description]
            filas = cursor.fetchall()
            conn.close()
            
            registros = [dict(zip(cols, f)) for f in filas]
            return {"registros": registros, "count": len(registros), "stat": stat, "dias": dias}
        except Exception as e:
            print(f"  Error consultando top jugadores: {e}")
            return {"registros": [], "count": 0, "error": str(e)}


# ──────────────────────────────────────────────
# Exports
# ──────────────────────────────────────────────

extractor = VideoDataExtractor()  # Instancia global


def extraer_jugador_desde_instruccion(instruccion: str) -> Optional[Dict]:
    """API pública: extrae y valida jugador."""
    return extractor.extraer_jugador(instruccion)


def obtener_datos_jugador(nombre_mapped: str, stat: str = "PTS", num_partidos: int = 20):
    """API pública: obtiene datos de jugador."""
    return extractor.datos_jugador_ultimos_partidos(nombre_mapped, stat, num_partidos)
