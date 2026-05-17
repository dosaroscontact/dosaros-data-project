"""
publish_analysis.py

Publica un análisis diario DOS AROS en la web.

Lee un .md de Downloads (o ruta indicada), genera frontmatter automáticamente,
lo mueve a content/analysis/YYYY/MM/, y opcionalmente hace commit + push.

Uso:
    python scripts/publish_analysis.py DOS_AROS_ANALISIS_16_MAYO_2026_V3.md
    python scripts/publish_analysis.py path/al/archivo.md
    python scripts/publish_analysis.py archivo.md --no-commit  # sin git
    python scripts/publish_analysis.py archivo.md --dry-run    # solo preview

Convenciones:
- Nombre de archivo input: DOS_AROS_ANALISIS_DD_MES_YYYY[_Vx].md
- Output: content/analysis/YYYY/MM/YYYY-MM-DD-slug.md
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from unicodedata import normalize

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).parent.parent
DOWNLOADS = Path.home() / "Downloads"
CONTENT_ROOT = PROJECT_ROOT / "content" / "analysis"

# Mapeo de meses ES → número
MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}

# Tags conocidos a detectar en el cuerpo
TAG_KEYWORDS = {
    "NBA": ["NBA", "Spurs", "Lakers", "Celtics", "Warriors", "Thunder", "Knicks", "Heat", "Bucks", "Timberwolves", "Wemby", "Wembanyama"],
    "WNBA": ["WNBA", "Caitlin Clark", "Paige Bueckers", "A'ja Wilson", "Angel Reese"],
    "EuroLeague": ["EuroLeague", "Euroliga", "Real Madrid", "Valencia Basket", "Olympiacos", "Panathinaikos", "Fenerbahçe", "Žalgiris"],
    "Europa": ["FIBA", "Liga Endesa", "ACB", "EuroCup", "BCL"],
    "LigaFemenina": ["Femenino", "Femenina", "Valencia Basket femenino", "Liga Femenina", "Awa Fam", "Roig Arena"],
    "Playoffs": ["Playoffs", "Game 1", "Game 2", "Game 3", "Game 4", "Game 5", "Game 6", "Game 7"],
    "FinalFour": ["Final Four", "Atenas"],
    "Finales": ["Finales del Oeste", "Finales del Este", "Conference Finals", "NBA Finals"],
}


def slugify(text: str) -> str:
    """Convierte texto a slug URL-friendly."""
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:60]


def extract_date(filename: str, content: str) -> datetime:
    """Extrae fecha del nombre de archivo o del contenido."""
    # Intentar desde filename: DOS_AROS_ANALISIS_DD_MES_YYYY
    m = re.search(r"(\d{1,2})_(\w+)_(\d{4})", filename, re.IGNORECASE)
    if m:
        day, month_name, year = m.group(1), m.group(2).lower(), m.group(3)
        if month_name in MESES_ES:
            return datetime(int(year), MESES_ES[month_name], int(day))

    # Intentar desde el primer H1: "# 🏀 DOS AROS — 16 de mayo de 2026"
    m = re.search(r"#\s*[^\n]*?(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", content)
    if m:
        day, month_name, year = m.group(1), m.group(2).lower(), m.group(3)
        if month_name in MESES_ES:
            return datetime(int(year), MESES_ES[month_name], int(day))

    # Fallback: hoy
    print("⚠️  No se pudo detectar fecha. Usando hoy.")
    return datetime.now()


def extract_sections(content: str) -> list[dict]:
    """Extrae secciones (H2) con icono y título."""
    sections = []
    pattern = r"^##\s+(\S+)?\s*([^\n]+)$"

    for match in re.finditer(pattern, content, re.MULTILINE):
        icon_or_word = match.group(1) or ""
        rest = match.group(2) or ""

        # Detectar si el primer "token" es un emoji
        if icon_or_word and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]", icon_or_word):
            icon = icon_or_word
            title_full = rest
        else:
            icon = ""
            title_full = f"{icon_or_word} {rest}".strip()

        # Separar título y subtítulo por "|" si existe
        if "|" in title_full:
            title, subtitle = [t.strip() for t in title_full.split("|", 1)]
        else:
            title = title_full.strip()
            subtitle = ""

        league = detect_league(icon, title)
        sections.append({
            "icon": icon,
            "title": clean_markdown_escapes(title),
            "subtitle": clean_markdown_escapes(subtitle),
            "league": league,
        })

    return sections


def detect_league(icon: str, title: str) -> str:
    """Detecta liga por título primero (más específico), luego por icono."""
    title_upper = title.upper()

    # Liga Femenina (España) — palabra clave o icono naranja
    if "FEMENINO" in title_upper or "FEMENINA" in title_upper or "🟠" in icon:
        return "Liga Femenina"
    # WNBA tiene prioridad sobre NBA (ambas usan bandera US)
    if "WNBA" in title_upper:
        return "WNBA"
    # Europa genérico vs EuroLeague específico
    if "EUROPA" in title_upper or "FIBA" in title_upper or "ACB" in title_upper:
        return "Europa"
    if "EUROLIGA" in title_upper or "EUROLEAGUE" in title_upper or "FINAL FOUR" in title_upper:
        return "EuroLeague"
    if "NBA" in title_upper or "FINALES" in title_upper or any(k in title for k in ["SPURS", "LAKERS", "Game"]):
        return "NBA"
    # Fallback por bandera (menos preciso)
    if "🇺🇸" in icon:
        return "NBA"
    if "🇪🇺" in icon:
        return "EuroLeague"
    return "General"


def detect_tags(content: str) -> list[str]:
    """Detecta tags basándose en palabras clave del contenido."""
    found = set()
    for tag, keywords in TAG_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", content, re.IGNORECASE):
                found.add(tag)
                break
    return sorted(found)


def extract_summary(content: str, max_len: int = 180) -> str:
    """Extrae primer párrafo no-encabezado como summary."""
    # Saltar el H1 y H2 inicial
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---") or line.startswith("*"):
            continue
        # Limpiar markdown básico
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        clean = re.sub(r"\*([^*]+)\*", r"\1", clean)
        clean = re.sub(r"\\([._-])", r"\1", clean)
        if len(clean) > max_len:
            clean = clean[:max_len].rsplit(" ", 1)[0] + "…"
        return clean
    return ""


def clean_markdown_escapes(text: str) -> str:
    """Elimina backslash escapes de markdown (\\- → -, \\. → .)."""
    return re.sub(r"\\([._\-\(\)\[\]])", r"\1", text)


def generate_title(sections: list[dict], date: datetime) -> str:
    """Genera título usando la primera sección (más limpio y enfocado)."""
    if not sections:
        return f"Análisis del {date.strftime('%d de %B de %Y')}"

    s = sections[0]
    title = clean_markdown_escapes(s["title"])

    # Si tiene subtitle descriptivo, usarlo: "SPURS vs THUNDER | Finales del Oeste"
    if s.get("subtitle"):
        subtitle = clean_markdown_escapes(s["subtitle"])
        return f"{title} — {subtitle}"

    return title


def yaml_escape(text: str) -> str:
    """Escapa string para YAML double-quoted: escapa comillas y backslashes."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_frontmatter(date: datetime, content: str, slug: str) -> str:
    """Construye el bloque frontmatter YAML."""
    sections = extract_sections(content)
    tags = detect_tags(content)
    summary = extract_summary(content)
    title = generate_title(sections, date)

    fm = ["---"]
    fm.append(f'date: "{date.strftime("%Y-%m-%d")}"')
    fm.append(f'title: "{yaml_escape(title)}"')
    fm.append(f"slug: {slug}")
    fm.append(f'summary: "{yaml_escape(summary)}"')
    fm.append(f"tags: [{', '.join(tags)}]")
    fm.append("sections:")
    for s in sections:
        fm.append(f"  - league: {s['league']}")
        if s["icon"]:
            fm.append(f'    icon: "{yaml_escape(s["icon"])}"')
        fm.append(f'    title: "{yaml_escape(s["title"])}"')
        if s["subtitle"]:
            fm.append(f'    subtitle: "{yaml_escape(s["subtitle"])}"')
    fm.append("published: true")
    fm.append("---")
    fm.append("")
    return "\n".join(fm)


def publish(input_path: Path, dry_run: bool = False, no_commit: bool = False) -> int:
    """Procesa el archivo y lo publica."""
    if not input_path.exists():
        print(f"❌ Archivo no encontrado: {input_path}")
        return 1

    print(f"📄 Procesando: {input_path.name}")
    content = input_path.read_text(encoding="utf-8")
    date = extract_date(input_path.name, content)

    # Generar slug desde primera sección
    sections = extract_sections(content)
    if sections:
        slug_text = sections[0]["title"].split("|")[0].strip()
        slug = f"{date.strftime('%Y-%m-%d')}-{slugify(slug_text)}"
    else:
        slug = date.strftime("%Y-%m-%d")

    # Verificar si ya tiene frontmatter
    if content.lstrip().startswith("---"):
        print("⚠️  El archivo ya tiene frontmatter. Se mantiene tal cual.")
        full_content = content
    else:
        frontmatter = build_frontmatter(date, content, slug)
        full_content = frontmatter + content

    # Ruta de destino
    output_dir = CONTENT_ROOT / date.strftime("%Y") / date.strftime("%m")
    output_path = output_dir / f"{slug}.md"

    print(f"📅 Fecha: {date.strftime('%Y-%m-%d')}")
    print(f"🏷️  Slug: {slug}")
    print(f"📂 Destino: {output_path.relative_to(PROJECT_ROOT)}")
    print(f"📊 Secciones detectadas: {len(sections)}")
    for s in sections:
        print(f"   - {s['icon']} [{s['league']}] {s['title']}")

    if dry_run:
        print("\n--- DRY RUN — Frontmatter generado ---\n")
        print(full_content[:800])
        print("\n[…]")
        return 0

    # Crear directorios
    output_dir.mkdir(parents=True, exist_ok=True)

    # Escribir
    output_path.write_text(full_content, encoding="utf-8")
    print(f"\n✅ Publicado: {output_path}")

    # Git commit + push opcional
    if not no_commit:
        rel_path = output_path.relative_to(PROJECT_ROOT)
        commit_msg = f"feat(analysis): Add daily analysis for {date.strftime('%Y-%m-%d')}\n\nSource: {input_path.name}"
        try:
            subprocess.run(["git", "add", str(rel_path)], cwd=PROJECT_ROOT, check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
            print("✅ Commit creado")

            push = input("¿Hacer git push? (s/N): ").strip().lower()
            if push in ("s", "si", "sí", "y", "yes"):
                subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
                print("✅ Push completado")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error en git: {e}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Publica análisis diario DOS AROS")
    parser.add_argument("filename", help="Nombre del archivo (en Downloads) o ruta completa")
    parser.add_argument("--dry-run", action="store_true", help="Solo preview, no escribir")
    parser.add_argument("--no-commit", action="store_true", help="No hacer git commit")
    args = parser.parse_args()

    # Resolver ruta del input
    input_path = Path(args.filename)
    if not input_path.is_absolute() and not input_path.exists():
        # Probar en Downloads
        candidate = DOWNLOADS / args.filename
        if candidate.exists():
            input_path = candidate

    return publish(input_path, dry_run=args.dry_run, no_commit=args.no_commit)


if __name__ == "__main__":
    sys.exit(main())
