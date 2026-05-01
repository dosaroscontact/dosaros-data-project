import sqlite3
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List

DB_PATH = "/mnt/nba_data/dosaros_local.db"

# Categorías de insights
CATEGORIES = {
    # NBA Originales (9)
    "nba_three_point": "NBA: Rendimiento en triples",
    "nba_efficiency": "NBA: Eficiencia de equipo",
    "nba_defense": "NBA: Defensa destacada",
    "nba_bench": "NBA: Banca de equipo",
    "nba_turnovers": "NBA: Pérdidas y balones",
    "nba_clutch": "NBA: Momentos decisivos",
    "nba_injuries": "NBA: Impacto de lesiones",
    "nba_streaks": "NBA: Rachas de equipos",
    "nba_young_stars": "NBA: Estrellas jóvenes",
    
    # EuroLeague Originales (7)
    "euro_scoring_leader": "EuroLeague: Goleador de la jornada",
    "euro_assists": "EuroLeague: Asistencias destacadas",
    "euro_rebounds": "EuroLeague: Rebotes dominantes",
    "euro_defensive_rating": "EuroLeague: Rating defensivo",
    "euro_bench_scoring": "EuroLeague: Banca productiva",
    "euro_turnover_battle": "EuroLeague: Batalla de posesiones",
    "euro_international_impact": "EuroLeague: Impacto internacional",
    
    # Nuevas Categorías (5)
    "team_analysis_offense": "Análisis de Equipos: Ofensiva",
    "team_analysis_defense": "Análisis de Equipos: Defensiva",
    "historical_comparison": "Comparativas Históricas",
    "playoff_projection": "Predicciones: Proyecciones Playoff",
    "tanking_race": "Tanking: Carrera draft",
    "playoff_matchups": "Cruces Playoff: Matchups y precedentes",
}

class InsightGenerator:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        if self.conn:
            self.conn.close()
    
    def is_category_published_recently(self, category: str, days: int = 21) -> bool:
        """Verifica si una categoría fue publicada en los últimos N días"""
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        cursor.execute(
            "SELECT COUNT(*) as count FROM published_insights WHERE category = ? AND published_date >= ?",
            (category, cutoff_date)
        )
        result = cursor.fetchone()
        return result['count'] > 0
    
    def get_available_categories(self) -> List[str]:
        """Retorna categorías disponibles (no publicadas en 21 días)"""
        available = []
        for category in CATEGORIES.keys():
            if not self.is_category_published_recently(category):
                available.append(category)
        return available
    
    def log_insight(self, category: str, insight_text: str, league: str = "NBA"):
        """Registra un insight como publicado"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO published_insights (category, insight_text, published_date, league) VALUES (?, ?, ?, ?)",
            (category, insight_text, datetime.now().date(), league)
        )
        self.conn.commit()
    
    # ==================== NBA INSIGHTS ====================
    
    def nba_three_point(self) -> Optional[str]:
        """NBA: Top rendimiento en triples"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3M, FG3A, 
                   ROUND(CAST(FG3M as FLOAT) / NULLIF(FG3A, 0) * 100, 1) as pct
            FROM nba_players_games
            WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
            AND FG3A >= 3
            ORDER BY FG3M DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"{result['PLAYER_NAME']} ({result['TEAM_ABBREVIATION']}) anotó {result['FG3M']} triples con {result['pct']}% de efectividad"
        return None
    
    def nba_efficiency(self) -> Optional[str]:
        """NBA: Eficiencia ofensiva de equipo"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, SUM(PTS) as total_pts, SUM(FGA) as total_fga,
                   ROUND(CAST(SUM(PTS) as FLOAT) / NULLIF(SUM(FGA), 0) * 100, 2) as efficiency
            FROM nba_players_games
            WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
            GROUP BY TEAM_NAME
            ORDER BY efficiency DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"{result['TEAM_NAME']}: {result['efficiency']}% de eficiencia ofensiva ({result['total_pts']} pts en {result['total_fga']} intentos)"
        return None
    
    def nba_defense(self) -> Optional[str]:
        """NBA: Defensa destacada (menos puntos permitidos)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT home_team_code as team, SUM(away_score) as points_allowed
            FROM games
            WHERE game_date = (SELECT MAX(game_date) FROM games)
            GROUP BY home_team_code
            UNION
            SELECT away_team_code, SUM(home_score)
            FROM games
            WHERE game_date = (SELECT MAX(game_date) FROM games)
            GROUP BY away_team_code
            ORDER BY points_allowed ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Defensa del día: {result['team']} permitió solo {result['points_allowed']} puntos"
        return None
    
    def nba_bench(self) -> Optional[str]:
        """NBA: Banca productiva"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, COUNT(DISTINCT PLAYER_NAME) as bench_players,
                   SUM(PTS) as bench_pts, SUM(REB) as bench_reb
            FROM nba_players_games
            WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
            AND MIN < 20
            GROUP BY TEAM_NAME
            ORDER BY bench_pts DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Banca en fuego: {result['TEAM_NAME']} anotó {result['bench_pts']} puntos con {result['bench_players']} jugadores"
        return None
    
    def nba_turnovers(self) -> Optional[str]:
        """NBA: Batalla de balones"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, SUM(TOV) as turnovers, SUM(STL) as steals
            FROM nba_players_games
            WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
            GROUP BY TEAM_NAME
            ORDER BY (SUM(STL) - SUM(TOV)) DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            balance = result['steals'] - result['turnovers']
            return f"{result['TEAM_NAME']}: balance de {balance} en pérdidas vs. robos"
        return None
    
    def nba_clutch(self) -> Optional[str]:
        """NBA: Momentos decisivos (últimos 2 minutos)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, COUNT(*) as clutch_plays
            FROM nba_pbp
            WHERE period = 4
            GROUP BY PLAYER_NAME, TEAM_ABBREVIATION
            ORDER BY clutch_plays DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Momento clave: {result['PLAYER_NAME']} ({result['TEAM_ABBREVIATION']}) en momentos decisivos"
        return None
    
    def nba_injuries(self) -> Optional[str]:
        """NBA: Impacto de lesiones en equipo"""
        return "🚨 Monitorea las lesiones clave que afectan la composición de los equipos"
    
    def nba_streaks(self) -> Optional[str]:
        """NBA: Rachas de victorias/derrotas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_ABBREVIATION, WL, COUNT(*) as consecutive
            FROM nba_players_games
            WHERE GAME_DATE >= (SELECT MAX(GAME_DATE) FROM nba_players_games) - INTERVAL '10 days'
            GROUP BY TEAM_ABBREVIATION, WL
            ORDER BY consecutive DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            status = "V" if result['WL'] == "W" else "D"
            return f"Racha: {result['TEAM_ABBREVIATION']} con {result['consecutive']} {status}"
        return None
    
    def nba_young_stars(self) -> Optional[str]:
        """NBA: Actuaciones de jóvenes talentos"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST
            FROM nba_players_games
            WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
            AND MIN > 20
            ORDER BY PTS DESC
            LIMIT 3
        """)
        results = cursor.fetchall()
        if results:
            player = results[0]
            return f"Joven talento: {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}) con {player['PTS']}pts, {player['REB']}reb, {player['AST']}ast"
        return None
    
    # ==================== EUROLEAGUE INSIGHTS ====================
    
    def euro_scoring_leader(self) -> Optional[str]:
        """EuroLeague: Goleador de la jornada"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT epg.player_id, ep.player_name, epg.pts
            FROM euro_players_games epg
            JOIN euro_players ep ON epg.player_id = ep.player_id
            ORDER BY epg.pts DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Goleador: {result['player_name']} anotó {result['pts']} puntos"
        return None
    
    def euro_assists(self) -> Optional[str]:
        """EuroLeague: Asistencias destacadas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT epg.player_id, ep.player_name, epg.ast
            FROM euro_players_games epg
            JOIN euro_players ep ON epg.player_id = ep.player_id
            ORDER BY epg.ast DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Asistencias: {result['player_name']} repartió {result['ast']} pases"
        return None
    
    def euro_rebounds(self) -> Optional[str]:
        """EuroLeague: Dominio en rebotes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT epg.player_id, ep.player_name, epg.reb
            FROM euro_players_games epg
            JOIN euro_players ep ON epg.player_id = ep.player_id
            ORDER BY epg.reb DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Rebotes: {result['player_name']} capturó {result['reb']} rebotes"
        return None
    
    def euro_defensive_rating(self) -> Optional[str]:
        """EuroLeague: Rating defensivo"""
        return "Análisis de eficiencia defensiva en EuroLeague"
    
    def euro_bench_scoring(self) -> Optional[str]:
        """EuroLeague: Banca productiva"""
        return "Impacto de la banca en competiciones europeas"
    
    def euro_turnover_battle(self) -> Optional[str]:
        """EuroLeague: Batalla de posesiones"""
        return "Análisis de eficiencia en manejo de balón"
    
    def euro_international_impact(self) -> Optional[str]:
        """EuroLeague: Impacto internacional"""
        return "Desempeño de jugadores internacionales destacados"
    
    # ==================== NUEVAS CATEGORÍAS ====================
    
    def team_analysis_offense(self) -> Optional[str]:
        """Análisis de Equipos: Ofensiva"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, AVG(PTS) as avg_pts, COUNT(*) as games,
                   ROUND(AVG(CAST(FGM as FLOAT) / NULLIF(FGA, 0) * 100), 1) as fg_pct
            FROM nba_players_games
            WHERE GAME_DATE >= (SELECT MAX(GAME_DATE) FROM nba_players_games) - INTERVAL '7 days'
            GROUP BY TEAM_NAME
            ORDER BY avg_pts DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Ofensiva en forma: {result['TEAM_NAME']} promedia {result['avg_pts']:.1f} pts con {result['fg_pct']}% FG en últimos 7 días"
        return None
    
    def team_analysis_defense(self) -> Optional[str]:
        """Análisis de Equipos: Defensiva"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT home_team_code, AVG(away_score) as pts_allowed
            FROM games
            WHERE game_date >= (SELECT MAX(game_date) FROM games) - INTERVAL '7 days'
            GROUP BY home_team_code
            ORDER BY pts_allowed ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Defensa sólida: {result['home_team_code']} permite solo {result['pts_allowed']:.1f} pts/juego en 7 días"
        return None
    
    def historical_comparison(self) -> Optional[str]:
        """Comparativas Históricas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SEASON_ID, TEAM_NAME, AVG(PTS) as avg_pts, COUNT(*) as games
            FROM nba_players_games
            GROUP BY SEASON_ID, TEAM_NAME
            ORDER BY SEASON_ID DESC, avg_pts DESC
            LIMIT 5
        """)
        results = cursor.fetchall()
        if results:
            current = results[0]
            return f"Comparativa histórica: {current['TEAM_NAME']} promedia {current['avg_pts']:.1f} pts en {current['SEASON_ID']}"
        return None
    
    def playoff_projection(self) -> Optional[str]:
        """Predicciones: Proyecciones Playoff"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, COUNT(CASE WHEN WL='W' THEN 1 END) as wins,
                   COUNT(CASE WHEN WL='L' THEN 1 END) as losses,
                   ROUND(100.0 * COUNT(CASE WHEN WL='W' THEN 1 END) / COUNT(*), 1) as win_pct
            FROM nba_players_games
            WHERE GAME_DATE >= (SELECT MAX(GAME_DATE) FROM nba_players_games) - INTERVAL '20 days'
            GROUP BY TEAM_NAME
            ORDER BY win_pct DESC
            LIMIT 3
        """)
        results = cursor.fetchall()
        if results:
            team = results[0]
            return f"Proyección playoff: {team['TEAM_NAME']} con {team['win_pct']}% winning rate, {team['wins']}-{team['losses']} en últimas 20 jornadas"
        return None
    
    def tanking_race(self) -> Optional[str]:
        """Tanking: Carrera por draft picks"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TEAM_NAME, COUNT(CASE WHEN WL='L' THEN 1 END) as losses,
                   ROUND(100.0 * COUNT(CASE WHEN WL='L' THEN 1 END) / COUNT(*), 1) as loss_pct
            FROM nba_players_games
            WHERE GAME_DATE >= (SELECT MAX(GAME_DATE) FROM nba_players_games) - INTERVAL '15 days'
            GROUP BY TEAM_NAME
            ORDER BY loss_pct DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return f"Carrera draft: {result['TEAM_NAME']} con {result['loss_pct']}% de pérdidas en últimas 15 jornadas"
        return None
    
    def playoff_matchups(self) -> Optional[str]:
        """Cruces Playoff: Matchups y precedentes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT home_team_code, away_team_code, COUNT(*) as meetings,
                   SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as home_wins
            FROM games
            WHERE game_date >= (SELECT MAX(game_date) FROM games) - INTERVAL '365 days'
            GROUP BY home_team_code, away_team_code
            ORDER BY meetings DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            away_wins = result['meetings'] - result['home_wins']
            return f"Precedentes: {result['home_team_code']} vs {result['away_team_code']} se enfrentaron {result['meetings']} veces, {result['home_wins']}-{away_wins} de local"
        return None
    
    # ==================== GENERADOR PRINCIPAL ====================
    
    def generate_random_insight(self, league: str = "NBA") -> Optional[Dict]:
        """Genera un insight aleatorio de categoría disponible"""
        available = self.get_available_categories()
        
        if not available:
            return {"error": "No hay categorías disponibles (todas publicadas en últimos 21 días)"}
        
        category = random.choice(available)
        insight_text = None
        method_name = category
        
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            insight_text = method()
        
        if insight_text:
            self.log_insight(category, insight_text, league)
            return {
                "category": category,
                "title": CATEGORIES[category],
                "insight": insight_text,
                "league": league
            }
        
        return {"error": f"No se pudo generar insight para {category}"}
    
    def generate_daily_insights(self, count: int = 2) -> List[Dict]:
        """Genera N insights para el día"""
        insights = []
        for _ in range(count):
            insight = self.generate_random_insight()
            if "error" not in insight:
                insights.append(insight)
        return insights


# ==================== MAIN ====================

if __name__ == "__main__":
    generator = InsightGenerator()
    generator.connect()
    
    # Generar 2 insights del día
    daily_insights = generator.generate_daily_insights(2)
    
    for insight in daily_insights:
        print(f"📊 {insight['title']}")
        print(f"   {insight['insight']}")
        print()
    
    generator.close()
