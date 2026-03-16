"""
Analizador de relaciones entre archivos JSON
=============================================
Coloca este script en la misma carpeta que tus archivos JSON y ejecútalo.
Genera un informe 'informe_esquema.txt' que puedes subir a Claude
para que te construya el esquema de base de datos.

Instalación previa (una sola vez):
    pip install pandas tqdm
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

try:
    import pandas as pd
    from tqdm import tqdm
except ImportError:
    print("Instalando dependencias...")
    os.system("pip install pandas tqdm")
    import pandas as pd
    from tqdm import tqdm


# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
JSON_FOLDER = "."          # Carpeta con los JSONs (. = misma carpeta que el script)
OUTPUT_FILE = "informe_esquema.txt"
MAX_SAMPLE_VALUES = 3    # Valores de muestra por columna
FK_MATCH_THRESHOLD = 0.3   # % mínimo de coincidencia para sugerir FK (0.0 - 1.0)
MAX_ROWS_TO_SCAN = 1000    # Máximo de filas a escanear por archivo (para rendimiento)
# ───────────────────────────────────────────────────────────────────────────────


def load_json(path: Path):
    """Carga un JSON que es array de objetos. Maneja encodings comunes."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            # Si es objeto raíz, busca la primera lista dentro
            for v in data.values():
                if isinstance(v, list) and len(v) > 0:
                    return v
            return [data]
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None


def infer_schema(records: list, max_rows: int) -> dict:
    """Extrae esquema: tipos, nulos, valores únicos de muestra."""
    sample = records[:max_rows]
    schema = {}

    all_keys = set()
    for r in sample:
        if isinstance(r, dict):
            all_keys.update(r.keys())

    for key in sorted(all_keys):
        values = [r.get(key) for r in sample if isinstance(r, dict)]
        non_null = [v for v in values if v is not None and v != "" and v != []]
        null_count = len(values) - len(non_null)

        # Tipo predominante
        types = set(type(v).__name__ for v in non_null)
        inferred_type = types.pop() if len(types) == 1 else "/".join(sorted(types))

        # Cardinalidad
        try:
            unique_vals = list({str(v) for v in non_null})
            n_unique = len(unique_vals)
            sample_vals = sorted(unique_vals[:MAX_SAMPLE_VALUES])
        except Exception:
            n_unique = "?"
            sample_vals = []

        # Detectar si parece ID (nombre + cardinalidad alta)
        looks_like_id = (
            re.search(r'(^id$|_id$|^id_|uuid|key|code)', key, re.IGNORECASE) is not None
            or (isinstance(n_unique, int) and len(non_null) > 10 and n_unique / max(len(non_null), 1) > 0.9)
        )

        schema[key] = {
            "type": inferred_type,
            "nulls": null_count,
            "total": len(values),
            "n_unique": n_unique,
            "sample": sample_vals,
            "looks_like_id": looks_like_id,
        }

    return schema


def detect_foreign_keys(tables: dict) -> list:
    """
    Compara columnas con aspecto de ID entre tablas.
    Retorna lista de posibles relaciones (tabla_a.col -> tabla_b.col).
    """
    # Recopilar columnas candidatas con sus valores únicos
    candidates = {}  # (table, col) -> set of string values

    for tname, info in tables.items():
        schema = info["schema"]
        records = info["records"]
        sample = records[:MAX_ROWS_TO_SCAN]

        for col, meta in schema.items():
            if meta["looks_like_id"] and isinstance(meta["n_unique"], int) and meta["n_unique"] > 1:
                vals = {str(r.get(col)) for r in sample if isinstance(r, dict) and r.get(col) is not None}
                candidates[(tname, col)] = vals

    # Buscar solapamientos
    relations = []
    items = list(candidates.items())

    for i in range(len(items)):
        (t1, c1), vals1 = items[i]
        for j in range(len(items)):
            if i == j:
                continue
            (t2, c2), vals2 = items[j]
            if t1 == t2:
                continue

            # ¿Qué % de vals1 aparece en vals2?
            if not vals1 or not vals2:
                continue
            overlap = len(vals1 & vals2) / len(vals1)

            if overlap >= FK_MATCH_THRESHOLD:
                relations.append({
                    "from_table": t1,
                    "from_col": c1,
                    "to_table": t2,
                    "to_col": c2,
                    "match_pct": round(overlap * 100, 1),
                })

    # Deduplicar (quitar pares inversos redundantes, conservar el de mayor match)
    seen = set()
    deduped = []
    for r in sorted(relations, key=lambda x: -x["match_pct"]):
        key = frozenset([(r["from_table"], r["from_col"]), (r["to_table"], r["to_col"])])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped


def write_report(tables: dict, relations: list, output: str):
    lines = []
    lines.append("=" * 70)
    lines.append("INFORME DE ESQUEMA JSON — para análisis con Claude")
    lines.append("=" * 70)
    lines.append(f"Archivos analizados: {len(tables)}\n")

    # ── Esquema por tabla ──
    lines.append("─" * 70)
    lines.append("ESQUEMAS POR ARCHIVO")
    lines.append("─" * 70)

    for tname, info in tables.items():
        schema = info["schema"]
        n_records = info["n_records"]
        lines.append(f"\n📄 TABLA: {tname}  ({n_records} registros)")
        lines.append(f"  {'CAMPO':<35} {'TIPO':<12} {'ÚNICOS':>8}  {'NULOS':>6}  ID?")
        lines.append(f"  {'─'*35} {'─'*12} {'─'*8}  {'─'*6}  ───")
        for col, meta in schema.items():
            id_flag = "✓" if meta["looks_like_id"] else ""
            lines.append(
                f"  {col:<35} {meta['type']:<12} {str(meta['n_unique']):>8}  {str(meta['nulls']):>6}  {id_flag}"
            )
            if meta["sample"]:
                #sample_str = ", ".join(str(v) for v in meta["sample"][:5])
                sample_str = ", ".join(str(v)[:30] for v in meta["sample"][:3])
                lines.append(f"  {'':35}   Muestra: {sample_str}")

    # ── Relaciones detectadas ──
    lines.append("\n")
    lines.append("─" * 70)
    lines.append("RELACIONES DETECTADAS (posibles Foreign Keys)")
    lines.append("─" * 70)

    if not relations:
        lines.append("\n⚠️  No se detectaron relaciones automáticamente.")
        lines.append("   Puede que los IDs usen formatos distintos o que el umbral sea muy alto.")
        lines.append(f"   Prueba bajando FK_MATCH_THRESHOLD (actualmente {FK_MATCH_THRESHOLD})")
    else:
        lines.append(f"\nSe encontraron {len(relations)} posibles relaciones:\n")
        for r in relations:
            lines.append(
                f"  {r['from_table']}.{r['from_col']}  →  {r['to_table']}.{r['to_col']}"
                f"   (coincidencia: {r['match_pct']}%)"
            )

    lines.append("\n" + "=" * 70)
    lines.append("FIN DEL INFORME — Sube este archivo a Claude")
    lines.append("=" * 70)

    report = "\n".join(lines)
    with open(output, "w", encoding="utf-8") as f:
        f.write(report)

    return report


def main():
    folder = Path(JSON_FOLDER)
    json_files = sorted(folder.glob("*.json"))

    if not json_files:
        print(f"❌ No se encontraron archivos .json en '{folder.resolve()}'")
        print("   Asegúrate de que el script está en la misma carpeta que los JSONs")
        return

    print(f"📂 Encontrados {len(json_files)} archivos JSON\n")

    tables = {}

    for path in tqdm(json_files, desc="Analizando archivos"):
        records = load_json(path)
        if records is None or len(records) == 0:
            print(f"  ⚠️  {path.name}: no se pudo cargar o está vacío")
            continue

        table_name = path.stem  # nombre sin extensión
        schema = infer_schema(records, MAX_ROWS_TO_SCAN)
        tables[table_name] = {
            "schema": schema,
            "records": records,
            "n_records": len(records),
        }

    print(f"\n🔍 Detectando relaciones entre tablas...")
    relations = detect_foreign_keys(tables)

    print(f"✅ {len(relations)} posibles relaciones encontradas")
    print(f"\n📝 Generando informe...")

    report = write_report(tables, relations, OUTPUT_FILE)

    print(f"\n{'='*50}")
    print(f"✅ Informe guardado en: {Path(OUTPUT_FILE).resolve()}")
    print(f"{'='*50}")
    print("\n➡️  Sube el archivo 'informe_esquema.txt' a Claude")
    print("   y pídele que genere el esquema SQL con las relaciones.\n")

    # Preview en consola
    print("\n── PREVIEW ──────────────────────────────────────")
    print("\n".join(report.split("\n")[:40]))
    if len(report.split("\n")) > 40:
        print("... (ver archivo completo)")


if __name__ == "__main__":
    main()
