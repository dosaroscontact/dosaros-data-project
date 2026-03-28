"""
avatar_prompt_generator.py — Genera prompts de imagen para el avatar Dos Aros
por equipo NBA / EuroLeague.

Uso directo (genera todos):
    python src/processors/avatar_prompt_generator.py --liga NBA
    python src/processors/avatar_prompt_generator.py --liga EUROLIGA
    python src/processors/avatar_prompt_generator.py --equipo LAL
    python src/processors/avatar_prompt_generator.py --todos

Desde código:
    from src.processors.avatar_prompt_generator import generar_prompt_avatar
    resultado = generar_prompt_avatar("LAL")
    print(resultado["prompt_completo"])
"""

import argparse
import os
import sqlite3

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# ──────────────────────────────────────────────
# Descripción base del avatar (LOCKED)
# ──────────────────────────────────────────────
AVATAR_BASE = (
    "Ultra-detailed Pixar-style 3D character, full-body, slightly angled 3/4 view. "
    "Male, ~35 years old, bald with perfectly shaved head, short well-groomed dark beard "
    "and mustache, warm olive skin tone. Wide natural smile showing clean white teeth. "
    "Wearing sleek black sunglasses fully covering the eyes (no transparency). "
    "Athletic build, realistic human proportions with subtle Pixar stylization "
    "(slightly larger head, clean facial features, smooth skin). "
    "Black modern smartwatch on left wrist, multiple thin dark beaded bracelets on right wrist. "
    "Pixar-quality 3D render, ultra-clean topology, smooth shading, vibrant colors. "
    "Studio cinematic lighting, soft key light + subtle rim light, realistic shadows. "
    "Ultra-realistic 3D, 8K, sharp focus, global illumination, subsurface scattering on skin, PBR. "
    "Solid chroma key green (#00FF00) background, perfectly uniform, no gradients, no shadows. "
    "Full body visible, centered, no cropping."
)

NEGATIVE_PROMPT = (
    "no extra accessories, no logo changes, no color variations, no text distortion, "
    "no background elements, no pose variation, no different clothing, no different number, "
    "no extra text, no room walls, no whiteboard, no cartoon flat style, no 2D illustration"
)

MIDJOURNEY_SUFFIX = "--ar 2:3 --v 6 --style raw --q 2 --s 250"

MARCA = "DOS AROS"

# ──────────────────────────────────────────────
# Fórmula maestra
# ──────────────────────────────────────────────
FORMULA = (
    "A cinematic, ultra-realistic, photorealistic full-body render of the Dos Aros avatar character "
    "(reference: {avatar_base}), "
    "in a [{postura}] position. "
    "He is wearing [{vestimenta}]. "
    "All clothing, accessories, and environmental elements are strictly colored with the official colors "
    "of the {team_name}: primary color {color_a}, secondary {color_b}, tertiary {color_c}{color_d_str}. "
    "The primary color is applied to the main clothes, secondary to details and trim, tertiary for accents. "
    "He is located in [{decorado}]. "
    "Integrate the text '{marca}' as a [{tipo_logo}], "
    "using bold graffiti-inspired lettering, recolored in the {team_name} colors "
    "(primary color for outline, secondary for fill)."
)


# ──────────────────────────────────────────────
# Consulta a BD
# ──────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _query_team(team_code: str, variacion: int = 1) -> dict | None:
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM avatar_teams WHERE team_code=? AND variacion_idx=?",
        (team_code.upper(), variacion)
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def _query_liga(liga: str) -> list[dict]:
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM avatar_teams WHERE liga=? ORDER BY team_code, variacion_idx",
        (liga.upper(),)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _query_todos() -> list[dict]:
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM avatar_teams ORDER BY liga, team_code, variacion_idx")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
# Construcción del prompt
# ──────────────────────────────────────────────

def _construir_prompt(equipo: dict) -> dict:
    color_d_str = (
        f", accent {equipo['color_d']}" if equipo.get("color_d") else ""
    )

    prompt = FORMULA.format(
        avatar_base=AVATAR_BASE,
        postura=equipo["postura"],
        vestimenta=equipo["vestimenta"],
        team_name=equipo["team_name"],
        color_a=equipo["color_a"],
        color_b=equipo["color_b"],
        color_c=equipo["color_c"],
        color_d_str=color_d_str,
        decorado=equipo["decorado"],
        marca=MARCA,
        tipo_logo=equipo["tipo_logo"],
    )

    return {
        "team_code":      equipo["team_code"],
        "liga":           equipo["liga"],
        "team_name":      equipo["team_name"],
        "variacion":      equipo["variacion_idx"],
        "colores":        {
            "primario":   equipo["color_a"],
            "secundario": equipo["color_b"],
            "terciario":  equipo["color_c"],
            "acento":     equipo.get("color_d"),
        },
        "prompt":           prompt,
        "negative_prompt":  NEGATIVE_PROMPT,
        "midjourney_suffix": MIDJOURNEY_SUFFIX,
        "prompt_completo":  f"{prompt}\n\nNegative prompt: {NEGATIVE_PROMPT}\n\n{MIDJOURNEY_SUFFIX}",
    }


# ──────────────────────────────────────────────
# API pública
# ──────────────────────────────────────────────

def generar_prompt_avatar(team_code: str, variacion: int = 1) -> dict | None:
    """
    Genera el prompt completo para un equipo concreto.

    Args:
        team_code : código del equipo (ej. 'LAL', 'MAD', 'BOS')
        variacion : índice de variación (1 = primera, 2 = segunda, etc.)

    Returns:
        dict con 'prompt', 'negative_prompt', 'midjourney_suffix', 'prompt_completo'
        None si el equipo no está en la BD.
    """
    equipo = _query_team(team_code, variacion)
    if not equipo:
        print(f"  Equipo '{team_code}' (var {variacion}) no encontrado en avatar_teams.")
        return None
    return _construir_prompt(equipo)


def generar_prompts_liga(liga: str) -> list[dict]:
    """Genera prompts para todos los equipos de una liga."""
    equipos = _query_liga(liga)
    if not equipos:
        print(f"  Sin equipos en liga '{liga}'.")
        return []
    return [_construir_prompt(e) for e in equipos]


def generar_prompts_todos() -> list[dict]:
    """Genera prompts para todos los equipos de la BD."""
    return [_construir_prompt(e) for e in _query_todos()]


# ──────────────────────────────────────────────
# Salida legible
# ──────────────────────────────────────────────

def _imprimir_prompt(r: dict):
    sep = "=" * 70
    print(f"\n{sep}")
    var_str = f" (var {r['variacion']})" if r["variacion"] > 1 else ""
    print(f"  {r['liga']} · {r['team_name']}{var_str}")
    print(sep)
    print(r["prompt_completo"])


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generador de prompts de avatar Dos Aros")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--equipo",   help="Código de equipo, ej: LAL")
    group.add_argument("--liga",     help="Liga completa: NBA o EUROLIGA")
    group.add_argument("--todos",    action="store_true", help="Todos los equipos")
    parser.add_argument("--variacion", type=int, default=1, help="Índice de variación (default: 1)")
    args = parser.parse_args()

    if args.equipo:
        r = generar_prompt_avatar(args.equipo, args.variacion)
        if r:
            _imprimir_prompt(r)

    elif args.liga:
        resultados = generar_prompts_liga(args.liga)
        print(f"\n{len(resultados)} prompts para {args.liga.upper()}:")
        for r in resultados:
            _imprimir_prompt(r)

    elif args.todos:
        resultados = generar_prompts_todos()
        print(f"\n{len(resultados)} prompts en total:")
        for r in resultados:
            _imprimir_prompt(r)


if __name__ == "__main__":
    main()
