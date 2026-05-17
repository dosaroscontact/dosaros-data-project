"""
sync_obsidian_to_claude.py

Sincroniza contenido de Obsidian vault (knowledge_base/) → CLAUDE.md

Lee archivos clave de Obsidian y los compila en un CLAUDE.md estructurado
para que Claude Code tenga siempre el contexto más reciente del proyecto.

Uso:
    python scripts/sync_obsidian_to_claude.py
    python scripts/sync_obsidian_to_claude.py --dry-run
    python scripts/sync_obsidian_to_claude.py --watch  # modo continuo (futuro)

Filosofía:
- Obsidian es la fuente de verdad
- CLAUDE.md es un export legible para IA
- No editar CLAUDE.md manualmente (será sobrescrito)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Forzar UTF-8 para stdout en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "knowledge_base"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"

# Archivos fuente del vault, en orden de aparición en CLAUDE.md
SOURCES = [
    ("Project Root/README.md", "📖 Proyecto", ["## 🎯 Objetivo", "## 🏗️ Stack"]),
    ("Project Root/STATUS.md", "📊 Estado Actual", ["## 🟢 Entornos Activos", "## 📦 Cobertura"]),
    ("Development/Environment Setup.md", "💻 Entornos", ["## 🥧 Raspberry Pi 4"]),
    ("Development/Commands.md", "⌨️ Comandos", ["## 🚀 Arranque", "## 📊 ETL"]),
    ("Architecture/System Design.md", "🏗️ Arquitectura", ["## 🏗️ Arquitectura"]),
    ("Data/Data Dictionary.md", "🗄️ Schema BD", ["## 🗄️ Tablas", "## ⚠️ Reglas SQL"]),
    ("Brand/Visual Identity.md", "🎨 Brand", ["## 🎨 Paleta", "## ✍️ Tipografías"]),
    ("Workflows/Daily Automation.md", "⏰ Automatización", ["## 📅 Cron Diario", "## 🤖 Bot"]),
]

HEADER_TEMPLATE = """# CLAUDE.md

> ⚠️ **AUTO-GENERADO desde Obsidian** — No editar manualmente.
> Fuente: `knowledge_base/` · Última sincronización: {timestamp}
> Para editar: modificar archivos en `knowledge_base/` y ejecutar `python scripts/sync_obsidian_to_claude.py`

---

## 📋 Proyecto
**Dos Aros** — Análisis comparativo NBA + EuroLeague.
*"Datos primero. Contexto después. Opinión al final."*

Stack: Raspberry Pi 4 · Python · SQLite · Next.js 15 · Telegram bot · Multi-LLM (Gemini/Groq/Claude)
→ Knowledge base completo: `knowledge_base/INDEX.md` (Obsidian vault)

---
"""

FOOTER_TEMPLATE = """

---

## 📚 Referencias en Obsidian Vault

Para contenido completo y actualizado, consultar:
- **Overview**: `knowledge_base/Project Root/README.md`
- **Estado actual**: `knowledge_base/Project Root/STATUS.md`
- **Comandos**: `knowledge_base/Development/Commands.md`
- **Setup entornos**: `knowledge_base/Development/Environment Setup.md`
- **Troubleshooting**: `knowledge_base/Development/Debugging Guide.md`
- **Arquitectura**: `knowledge_base/Architecture/System Design.md`
- **ADRs**: `knowledge_base/Architecture/Decisions Log.md`
- **Brand**: `knowledge_base/Brand/Visual Identity.md`
- **Avatar**: `knowledge_base/Brand/Avatar System.md`
- **Data dictionary**: `knowledge_base/Data/Data Dictionary.md`
- **ETL**: `knowledge_base/Data/ETL Processes.md`
- **Workflows**: `knowledge_base/Workflows/Daily Automation.md`

---

**Generado por**: `scripts/sync_obsidian_to_claude.py`
**Para regenerar**: `python scripts/sync_obsidian_to_claude.py`
"""


def extract_sections(file_path: Path, section_filters: list[str]) -> str:
    """
    Extrae secciones específicas de un archivo markdown.

    Args:
        file_path: Ruta al archivo .md
        section_filters: Lista de encabezados a extraer (ej: ["## Setup", "## Comandos"])

    Returns:
        Texto markdown con las secciones filtradas
    """
    if not file_path.exists():
        return f"⚠️ Archivo no encontrado: `{file_path.relative_to(PROJECT_ROOT)}`\n"

    content = file_path.read_text(encoding="utf-8")

    # Si no hay filtros, devolver todo (después del primer ##)
    if not section_filters:
        return content

    # Extraer solo secciones que matchean
    result = []
    lines = content.split("\n")
    capturing = False
    current_section_level = 0

    for line in lines:
        # Detectar inicio de sección que matchea
        for filter_header in section_filters:
            if line.startswith(filter_header):
                capturing = True
                current_section_level = line.count("#", 0, line.index(" "))
                result.append(line)
                break
        else:
            # Si estamos capturando, verificar si llegamos a otra sección del mismo nivel
            if capturing and line.startswith("#"):
                line_level = len(line) - len(line.lstrip("#"))
                if line_level <= current_section_level:
                    capturing = False
                    continue

            if capturing:
                result.append(line)

    return "\n".join(result)


def strip_obsidian_links(text: str) -> str:
    """
    Convierte links de Obsidian [[file|alias]] o [[file]] a texto plano legible.
    """
    # [[file|alias]] → alias
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    # [[file]] → file
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    return text


def build_claude_md() -> str:
    """Construye el contenido completo de CLAUDE.md desde Obsidian."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = [HEADER_TEMPLATE.format(timestamp=timestamp)]

    for source_path, section_title, filters in SOURCES:
        file_path = VAULT_PATH / source_path

        output.append(f"\n## {section_title}")
        output.append(f"*Fuente: `knowledge_base/{source_path}`*\n")

        content = extract_sections(file_path, filters)
        content = strip_obsidian_links(content)

        # Bajar 1 nivel todos los headers para evitar conflicto con ##
        content = re.sub(r"^## ", "### ", content, flags=re.MULTILINE)
        content = re.sub(r"^### ", "#### ", content, flags=re.MULTILINE)

        output.append(content)
        output.append("\n---\n")

    output.append(FOOTER_TEMPLATE)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Sincroniza Obsidian → CLAUDE.md")
    parser.add_argument("--dry-run", action="store_true", help="No escribir, solo mostrar")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print(f"🔄 Sincronizando {VAULT_PATH} → {CLAUDE_MD}")

    if not VAULT_PATH.exists():
        print(f"❌ ERROR: Vault no encontrado en {VAULT_PATH}")
        return 1

    content = build_claude_md()

    if args.dry_run:
        print("\n--- DRY RUN — Contenido generado ---\n")
        print(content[:2000] + "\n...\n" + content[-500:])
        print(f"\n📊 Tamaño total: {len(content)} caracteres")
        return 0

    # Backup del CLAUDE.md actual
    if CLAUDE_MD.exists():
        backup = CLAUDE_MD.with_suffix(".md.bak")
        backup.write_text(CLAUDE_MD.read_text(encoding="utf-8"), encoding="utf-8")
        if args.verbose:
            print(f"💾 Backup creado: {backup}")

    # Escribir nuevo CLAUDE.md
    CLAUDE_MD.write_text(content, encoding="utf-8")
    print(f"✅ CLAUDE.md actualizado ({len(content)} caracteres)")
    print(f"📁 Fuentes procesadas: {len(SOURCES)}")

    return 0


if __name__ == "__main__":
    exit(main())
