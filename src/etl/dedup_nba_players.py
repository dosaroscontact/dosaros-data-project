"""
dedup_nba_players.py — Elimina duplicados en nba_players_games y nba_games

Uso:
    python src/etl/dedup_nba_players.py

Proceso para cada tabla:
  1. Cuenta registros totales y duplicados
  2. Crea tabla _clean con el primer registro por clave única
  3. Renombra original → _backup
  4. Renombra _clean → tabla original
  5. Añade UNIQUE constraint en la nueva tabla
"""

import sqlite3

DB_PATH = "/mnt/nba_data/dosaros_local.db"


def dedup_tabla(conn, tabla, clave_cols):
    """
    Elimina duplicados de `tabla` conservando el primer registro
    por la combinación de columnas en `clave_cols`.
    """
    clave = ", ".join(clave_cols)
    tabla_clean  = f"{tabla}_clean"
    tabla_backup = f"{tabla}_backup"

    cursor = conn.cursor()

    # ── Diagnóstico ──────────────────────────────────────────────
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    total = cursor.fetchone()[0]

    duplicados_sql = f"""
        SELECT COUNT(*) FROM {tabla}
        WHERE rowid NOT IN (
            SELECT MIN(rowid) FROM {tabla} GROUP BY {clave}
        )
    """
    cursor.execute(duplicados_sql)
    duplicados = cursor.fetchone()[0]
    unicos = total - duplicados

    print(f"\n{'='*55}")
    print(f"Tabla: {tabla}")
    print(f"  Total registros  : {total:,}")
    print(f"  Duplicados       : {duplicados:,}")
    print(f"  Únicos           : {unicos:,}")

    if duplicados == 0:
        print("  Sin duplicados. No se requiere acción.")
        # Verificar si ya existe la constraint UNIQUE
        _asegurar_unique(cursor, tabla, clave_cols)
        conn.commit()
        return

    # ── Limpiar tablas temporales previas si existen ─────────────
    cursor.execute(f"DROP TABLE IF EXISTS {tabla_clean}")
    cursor.execute(f"DROP TABLE IF EXISTS {tabla_backup}")

    # ── Obtener columnas de la tabla original ─────────────────────
    cursor.execute(f"PRAGMA table_info({tabla})")
    cols_info = cursor.fetchall()
    col_names = [c[1] for c in cols_info]
    col_types = {c[1]: c[2] for c in cols_info}

    cols_def = ", ".join(
        f"{c} {col_types[c]}" for c in col_names
    )
    unique_constraint = f", UNIQUE ({clave})"

    # ── Crear tabla limpia con constraint ────────────────────────
    cursor.execute(f"""
        CREATE TABLE {tabla_clean} (
            {cols_def}
            {unique_constraint}
        )
    """)

    cols_list = ", ".join(col_names)
    cursor.execute(f"""
        INSERT INTO {tabla_clean} ({cols_list})
        SELECT {cols_list} FROM {tabla}
        WHERE rowid IN (
            SELECT MIN(rowid) FROM {tabla} GROUP BY {clave}
        )
    """)

    cursor.execute(f"SELECT COUNT(*) FROM {tabla_clean}")
    insertados = cursor.fetchone()[0]

    # ── Renombrar tablas ─────────────────────────────────────────
    cursor.execute(f"ALTER TABLE {tabla} RENAME TO {tabla_backup}")
    cursor.execute(f"ALTER TABLE {tabla_clean} RENAME TO {tabla}")

    conn.commit()

    print(f"  Registros en tabla limpia : {insertados:,}")
    print(f"  Backup guardado en        : {tabla_backup}")
    print(f"  UNIQUE ({clave}) aplicado.")


def _asegurar_unique(cursor, tabla, clave_cols):
    """Crea índice UNIQUE si no existe ya."""
    clave = ", ".join(clave_cols)
    idx_name = f"idx_unique_{'_'.join(c.lower() for c in clave_cols)}_{tabla}"
    cursor.execute(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS {idx_name}
        ON {tabla} ({clave})
    """)


def main():
    print(f"DB: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    # ── nba_players_games: clave (GAME_ID, PLAYER_ID) ────────────
    dedup_tabla(conn, "nba_players_games", ["GAME_ID", "PLAYER_ID"])

    # ── nba_games: clave (GAME_ID, TEAM_ID) ─────────────────────
    dedup_tabla(conn, "nba_games", ["GAME_ID", "TEAM_ID"])

    conn.close()
    print(f"\nFin.")


if __name__ == "__main__":
    main()
