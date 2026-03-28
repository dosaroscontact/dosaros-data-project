"""
export_avatar_prompts.py — Exporta todos los prompts de avatar a TXT y CSV.

Uso:
    python scripts/export_avatar_prompts.py           # todos
    python scripts/export_avatar_prompts.py --liga NBA
    python scripts/export_avatar_prompts.py --liga EUROLIGA
    python scripts/export_avatar_prompts.py --equipo LAL

Genera dos archivos en assets/avatars/prompts/:
    - prompts_completos.txt  → listo para pegar en Midjourney o ImageFX
    - prompts_tabla.csv      → tabla con team_code, variacion, prompt_completo
"""

import argparse
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.processors.avatar_prompt_generator import (
    generar_prompt_avatar,
    generar_prompts_liga,
    generar_prompts_todos,
)

OUTPUT_DIR = Path(__file__).parents[1] / "assets" / "avatars" / "prompts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def exportar(resultados: list, sufijo: str = "todos"):
    if not resultados:
        print("Sin resultados para exportar.")
        return

    # ── TXT para Midjourney / ImageFX ────────────────────────────────────────
    txt_path = OUTPUT_DIR / f"prompts_{sufijo}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for r in resultados:
            var_str = f"_v{r['variacion']}" if r["variacion"] > 1 else ""
            f.write(f"# {r['liga']} — {r['team_name']}{var_str}\n")
            f.write(r["prompt_completo"])
            f.write("\n\n" + "─" * 80 + "\n\n")

    print(f"✅ TXT exportado: {txt_path}  ({len(resultados)} prompts)")

    # ── CSV con columnas separadas ────────────────────────────────────────────
    csv_path = OUTPUT_DIR / f"prompts_{sufijo}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "team_code", "liga", "team_name", "variacion",
            "color_primario", "color_secundario",
            "prompt", "negative_prompt", "midjourney_suffix",
        ])
        writer.writeheader()
        for r in resultados:
            writer.writerow({
                "team_code":       r["team_code"],
                "liga":            r["liga"],
                "team_name":       r["team_name"],
                "variacion":       r["variacion"],
                "color_primario":  r["colores"]["primario"],
                "color_secundario":r["colores"]["secundario"],
                "prompt":          r["prompt"],
                "negative_prompt": r["negative_prompt"],
                "midjourney_suffix":r["midjourney_suffix"],
            })

    print(f"✅ CSV exportado: {csv_path}")
    print(f"\nResumen por liga:")
    ligas = {}
    for r in resultados:
        ligas[r["liga"]] = ligas.get(r["liga"], 0) + 1
    for liga, n in sorted(ligas.items()):
        print(f"  {liga}: {n} prompts")


def main():
    parser = argparse.ArgumentParser(description="Exportar prompts de avatar Dos Aros")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--liga",   help="NBA o EUROLIGA")
    group.add_argument("--equipo", help="Código equipo, ej: LAL")
    parser.add_argument("--variacion", type=int, default=0,
                        help="Variación concreta (0 = todas)")
    args = parser.parse_args()

    if args.equipo:
        r = generar_prompt_avatar(args.equipo, args.variacion or 1)
        resultados = [r] if r else []
        sufijo = args.equipo.upper()
    elif args.liga:
        resultados = generar_prompts_liga(args.liga)
        sufijo = args.liga.upper()
    else:
        resultados = generar_prompts_todos()
        sufijo = "todos"

    exportar(resultados, sufijo)


if __name__ == "__main__":
    main()
