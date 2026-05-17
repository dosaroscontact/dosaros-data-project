# 🔁 Sync Obsidian to Claude Code

**Objetivo**: Mantener `CLAUDE.md` siempre sincronizado con el knowledge base de Obsidian.

---

## 🎯 Arquitectura

```
┌─────────────────────────────────────────┐
│  knowledge_base/ (Obsidian Vault)       │
│  Source of Truth                        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  scripts/sync_obsidian_to_claude.py    │
│  Compila secciones clave                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  CLAUDE.md (Auto-generado)              │
│  Read-only para usuario                 │
│  Claude Code lo lee al iniciar          │
└─────────────────────────────────────────┘
```

---

## 🛠️ Componentes

### 1. Script Python: `scripts/sync_obsidian_to_claude.py`

**Función**: Lee archivos seleccionados de Obsidian y compila CLAUDE.md.

**Uso**:
```bash
# Modo normal (actualiza CLAUDE.md)
python scripts/sync_obsidian_to_claude.py

# Modo dry-run (solo preview)
python scripts/sync_obsidian_to_claude.py --dry-run

# Verbose
python scripts/sync_obsidian_to_claude.py --verbose
```

**Características**:
- Crea backup automático en `CLAUDE.md.bak`
- Compila desde 8 archivos clave de Obsidian
- Strip links `[[file|alias]]` → `alias`
- Output UTF-8 compatible Windows

**Archivos fuente** (en orden):
1. `Project Root/README.md` — Overview
2. `Project Root/STATUS.md` — Estado actual
3. `Development/Environment Setup.md` — Setup Pi
4. `Development/Commands.md` — Comandos
5. `Architecture/System Design.md` — Arquitectura
6. `Data/Data Dictionary.md` — Schema BD
7. `Brand/Visual Identity.md` — Paleta + fuentes
8. `Workflows/Daily Automation.md` — Cron + Bot

---

### 2. GitHub Action: `.github/workflows/sync-obsidian.yml`

**Trigger**: Push a `main` que modifique `knowledge_base/**` o el script.

**Acciones**:
1. Checkout del repo
2. Setup Python 3.11
3. Ejecutar script de sync
4. Si CLAUDE.md cambió → commit + push automático

**Manual**: Se puede ejecutar desde GitHub UI con "Run workflow".

---

## 📋 Workflow Diario

### Escenario: Cambio de configuración Pi

1. **Tú editas en Obsidian**:
   - Abres `knowledge_base/Development/Environment Setup.md`
   - Cambias IP del Pi: `192.168.1.136` → `192.168.1.200`
   - Guardas (Obsidian auto-save)

2. **Commit a Git**:
   ```bash
   git add knowledge_base/Development/Environment\ Setup.md
   git commit -m "docs: Update Pi IP address"
   git push origin main
   ```

3. **GitHub Action ejecuta**:
   - Detecta cambio en `knowledge_base/**`
   - Corre `sync_obsidian_to_claude.py`
   - Genera nuevo CLAUDE.md con IP actualizada
   - Commit automático: `chore: Auto-sync CLAUDE.md from Obsidian vault`

4. **Próxima sesión Claude Code**:
   - Lee CLAUDE.md actualizado
   - Tiene la nueva IP del Pi
   - No necesita preguntar

---

## 🔄 Sincronización Manual

Si no quieres esperar a GitHub Action:

```bash
# 1. Editar en Obsidian
# 2. Sincronizar localmente
python scripts/sync_obsidian_to_claude.py

# 3. Verificar
diff CLAUDE.md CLAUDE.md.bak

# 4. Commit ambos
git add knowledge_base/ CLAUDE.md
git commit -m "docs: Update environment + sync"
git push origin main
```

---

## ⚠️ Reglas Importantes

### NO editar CLAUDE.md directamente
- Será sobrescrito en la próxima sincronización
- El warning al inicio del archivo lo indica claramente
- Los backups quedan en `CLAUDE.md.bak`

### SÍ editar en Obsidian
- Es la fuente de verdad
- Soporta links bidireccionales `[[file]]`
- Mejor UX para escribir

### Filtros de Sección
- El script extrae solo secciones específicas de cada archivo
- Definidas en `SOURCES` dentro del script
- Si necesitas más contenido en CLAUDE.md, ajusta los filtros

---

## 🐛 Troubleshooting

### CLAUDE.md no se actualiza después de commit
- Verificar que el cambio toca `knowledge_base/**`
- Ver GitHub Actions en repo → Sync Obsidian to CLAUDE.md
- Si falla: ejecutar manualmente y push

### Caracteres raros en CLAUDE.md
- El script fuerza UTF-8 en Windows
- Si hay errores, ejecutar con `PYTHONIOENCODING=utf-8`

### Secciones faltantes
- Editar `SOURCES` en `scripts/sync_obsidian_to_claude.py`
- Añadir tuple `(path, title, [filters])`
- Re-ejecutar

---

## 🔗 Referencias

- Script: `scripts/sync_obsidian_to_claude.py`
- Workflow: `.github/workflows/sync-obsidian.yml`
- [[../Architecture/Decisions Log#ADR-006|ADR-006: Obsidian como Knowledge Base]]
- [[../Project Root/STATUS|📊 STATUS]]
