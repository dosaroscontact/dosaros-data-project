"""
batch_avatar_generator.py — Genera imágenes del avatar Dos Aros en lote.

Usa Together AI (Flux.1 Schnell) o Pollinations (gratis) según disponibilidad.
Las imágenes se guardan en assets/avatars/generated/{liga}/{team_code}_v{N}.png

Uso:
    python scripts/batch_avatar_generator.py --liga NBA
    python scripts/batch_avatar_generator.py --liga EUROLIGA
    python scripts/batch_avatar_generator.py --equipo LAL
    python scripts/batch_avatar_generator.py --todos
    python scripts/batch_avatar_generator.py --liga NBA --provider pollinations
    python scripts/batch_avatar_generator.py --liga NBA --pausa 8

Opciones:
    --provider   together (default) | pollinations
    --pausa      segundos entre requests (default: 5)
    --sobreescribir  regenera aunque ya exista el archivo
"""

import argparse
import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.processors.avatar_prompt_generator import (
    generar_prompt_avatar,
    generar_prompts_liga,
    generar_prompts_todos,
)

OUTPUT_BASE = Path(__file__).parents[1] / "assets" / "avatars" / "generated"


# ──────────────────────────────────────────────
# Generadores por proveedor
# ──────────────────────────────────────────────

def _generar_together(prompt: str) -> bytes:
    """Genera imagen con Together AI (Flux.1 Schnell) y retorna bytes PNG."""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY no configurada en .env")

    model = os.getenv("TOGETHER_MODEL", "black-forest-labs/FLUX.1-schnell")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model":  model,
        "prompt": prompt,
        "steps":  4,           # Schnell: 1-4 pasos
        "width":  768,
        "height": 1152,        # ratio 2:3
        "n":      1,
    }
    resp = requests.post(
        "https://api.together.xyz/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    # Puede volver URL o b64
    url = data["data"][0].get("url")
    if url:
        img_resp = requests.get(url, timeout=30)
        img_resp.raise_for_status()
        return img_resp.content

    import base64
    b64 = data["data"][0].get("b64_json")
    if b64:
        return base64.b64decode(b64)

    raise ValueError(f"Together: respuesta inesperada: {data}")


def _generar_pollinations(prompt: str) -> bytes:
    """Genera imagen con Pollinations (gratis, sin clave) y retorna bytes."""
    # Limpiar el prompt: sustituir '/' para que no rompa la URL path,
    # y limitar longitud para evitar URLs demasiado largas.
    prompt_limpio = prompt[:600].replace("/", "-").replace("\\", "-")
    encoded = quote(prompt_limpio, safe="")
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=768&height=1152&model=flux&nologo=true&seed={abs(hash(prompt)) % 99999}"
    )
    resp = requests.get(url, timeout=90)
    resp.raise_for_status()
    return resp.content


# ──────────────────────────────────────────────
# Lógica principal
# ──────────────────────────────────────────────

def generar_imagen(resultado: dict, provider: str, sobreescribir: bool, pausa: float) -> bool:
    """
    Genera y guarda una imagen para un equipo.
    Retorna True si se generó, False si se saltó o falló.
    """
    liga      = resultado["liga"]
    team_code = resultado["team_code"]
    variacion = resultado["variacion"]
    team_name = resultado["team_name"]

    # Ruta de destino
    out_dir = OUTPUT_BASE / liga
    out_dir.mkdir(parents=True, exist_ok=True)
    var_str  = f"_v{variacion}" if variacion > 1 else ""
    out_path = out_dir / f"{team_code}{var_str}.png"

    if out_path.exists() and not sobreescribir:
        print(f"  ⏭  {team_code}{var_str} — ya existe, saltando")
        return False

    print(f"  🎨 {liga} · {team_name}{var_str} ({provider})...", end=" ", flush=True)

    # Usar solo el prompt principal (sin negative ni suffix para APIs que no lo soportan)
    prompt = resultado["prompt"]

    try:
        if provider == "together":
            img_bytes = _generar_together(prompt)
        else:
            img_bytes = _generar_pollinations(prompt)

        out_path.write_bytes(img_bytes)
        kb = len(img_bytes) // 1024
        print(f"✅ {kb} KB → {out_path.name}")

        if pausa > 0:
            time.sleep(pausa)
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def procesar_lote(resultados: list, provider: str, sobreescribir: bool, pausa: float):
    total     = len(resultados)
    generados = 0
    saltados  = 0
    errores   = 0

    print(f"\n{'='*60}")
    print(f"Batch avatar generator — {total} imágenes · proveedor: {provider}")
    print(f"{'='*60}\n")

    for i, r in enumerate(resultados, 1):
        print(f"[{i}/{total}]", end=" ")
        ok = generar_imagen(r, provider, sobreescribir, pausa)
        if ok:
            generados += 1
        elif not (OUTPUT_BASE / r["liga"] / f"{r['team_code']}.png").exists():
            errores += 1
        else:
            saltados += 1

    print(f"\n{'='*60}")
    print(f"Resumen: {generados} generadas · {saltados} saltadas · {errores} errores")
    print(f"Carpeta: {OUTPUT_BASE}")
    print(f"{'='*60}")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generador batch de avatares Dos Aros")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--liga",   help="NBA o EUROLIGA")
    group.add_argument("--equipo", help="Código equipo, ej: LAL")
    group.add_argument("--todos",  action="store_true")
    parser.add_argument("--variacion", type=int, default=0,
                        help="Variación concreta (0 = todas)")
    parser.add_argument("--provider", choices=["together", "pollinations"],
                        default="pollinations",
                        help="Proveedor de imagen (default: pollinations)")
    parser.add_argument("--pausa", type=float, default=5,
                        help="Segundos entre requests (default: 5)")
    parser.add_argument("--sobreescribir", action="store_true",
                        help="Regenera aunque ya exista el archivo")
    args = parser.parse_args()

    if args.equipo:
        var = args.variacion or 1
        r = generar_prompt_avatar(args.equipo, var)
        resultados = [r] if r else []
    elif args.liga:
        resultados = generar_prompts_liga(args.liga)
        if args.variacion:
            resultados = [r for r in resultados if r["variacion"] == args.variacion]
    else:
        resultados = generar_prompts_todos()

    if not resultados:
        print("Sin prompts para procesar.")
        return

    procesar_lote(resultados, args.provider, args.sobreescribir, args.pausa)


if __name__ == "__main__":
    main()
