# Skill: video-generation

Genera composiciones Remotion TSX para el bot Dos Aros y las renderiza como MP4.

## Cuándo usar

Cuando el usuario pida generar un video de baloncesto basado en datos NBA o Euroliga.
Ejemplos: "genera un video con los top 3 tiradores", "crea un TikTok con el MVP de la semana".

## Flujo

1. `VideoGenerator._extraer_contexto(instruccion)` → JSON con tipo, liga, template, estadística
2. `VideoGenerator._consultar_datos(contexto)` → SQL sobre `nba_players_games` / `euro_players_games`
3. `VideoGenerator._construir_prompt_tsx(...)` → mega-prompt con datos y paleta Dos Aros
4. Claude/Gemini genera composición TSX para Editor Pro Max
5. TSX se guarda en `editor_pro_max/src/compositions/`
6. `npx remotion render` produce el MP4
7. Bot envía el MP4 por Telegram vía `bot_manager.enviar_video()`

## Archivos clave

| Archivo | Rol |
|---------|-----|
| `src/integrations/video_generator/video_generator.py` | Clase principal |
| `src/integrations/video_generator/__init__.py` | Re-exporta VideoGenerator |
| `src/automation/bot_consultas.py` | `_procesar_comando_video()` — manejo del comando /video |
| `src/automation/bot_manager.py` | `enviar_video()` — envío del MP4 |
| `automation/video_generator.py` | Borrador original (referencia) |

## Dependencias externas

- **Editor Pro Max**: clonar en la raíz del proyecto
  ```
  git clone https://github.com/Hainrixz/editor-pro-max.git
  cd editor_pro_max && npm install
  ```
- **Remotion**: instalado al hacer `npm install` dentro de editor_pro_max
- **ffmpeg**: `sudo apt-get install ffmpeg`

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `EDITOR_PRO_MAX_PATH` | Path absoluto a Editor Pro Max (opcional, autodetecta) |
| `LOCAL_DB` | Path a la BD SQLite (default: `/mnt/nba_data/dosaros_local.db`) |

## Uso desde Telegram

```
/video Top 3 tiradores de 3 puntos NBA esta semana
/v Resultado último partido Celtics
/video Comparativa puntos Luka vs SGA temporada 2024
```

## Paleta de colores Dos Aros para composiciones TSX

```typescript
const BRAND = {
  azul:    "#0D1321",  // fondo principal, titulares
  magenta: "#B1005A",  // dato destacado
  naranja: "#F28C28",  // detalles, iconos
  gris:    "#E6E8EE",  // separadores
  mint:    "#88D4AB",  // positivo / makes
  coral:   "#FF8787",  // negativo / misses
  blanco:  "#FFFFFF",  // fondo posts
};
```

## Tablas BD disponibles (para SQL en composiciones)

- `nba_players_games` — columnas UPPERCASE (PLAYER_NAME, TEAM_ABBREVIATION, PTS, FG3M, AST, REB, GAME_DATE…)
- `euro_players_games` — columnas lowercase (player_id, team_id, pts, reb, ast, game_id)
- `nba_games` — UPPERCASE (TEAM_ABBREVIATION, GAME_DATE, MATCHUP, WL, PTS…)
- `euro_games` — lowercase (game_id, date, home_team, away_team, score_home, score_away)

**Regla SQL crítica**: nunca usar `YEAR()`, usar `SEASON_ID LIKE '2024%'` o `date()`.
