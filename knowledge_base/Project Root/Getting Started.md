# 🚀 Getting Started — Cómo Usar el Nuevo Sistema

Guía de inicio rápido para trabajar con DOS AROS + Obsidian como knowledge base.

---

## 🎯 Filosofía del Sistema

> **Obsidian es la fuente única de verdad.**
> **CLAUDE.md se auto-genera. Nunca lo edites manualmente.**

```
Tu mente
    ↓
Obsidian (knowledge_base/)
    ↓
Script de sincronización
    ↓
CLAUDE.md (auto-generado)
    ↓
Claude Code lo lee al iniciar sesión
```

---

## 👤 Para Ti (Usuario)

### Edición de Documentación

#### ✅ Hacer
1. Abrir Obsidian apuntando a `C:\Users\rover\dosaros-data-project\knowledge_base\`
2. Editar las notas correspondientes
3. Usar links `[[file]]` para vincular conceptos
4. Guardar (Obsidian auto-save)
5. Commit + push a Git → GitHub Action sincroniza CLAUDE.md

#### ❌ Evitar
- NO editar `CLAUDE.md` directamente (será sobrescrito)
- NO duplicar info entre `CLAUDE.md` y notas
- NO crear `.md` random en raíz del proyecto

### Flujo de Trabajo Típico

#### Caso 1: Cambias configuración de Pi
```
Editas: knowledge_base/Development/Environment Setup.md
       → Cambias IP del Pi
Commit: git add knowledge_base/ && git commit -m "docs: New Pi IP"
Push:   git push origin main
Result: GitHub Action regenera CLAUDE.md automáticamente
```

#### Caso 2: Documentas decisión arquitectónica
```
Editas: knowledge_base/Architecture/Decisions Log.md
       → Añades nuevo ADR
Sync:   python scripts/sync_obsidian_to_claude.py  # opcional, lo hace GH Action
Commit: git add . && git commit -m "docs: ADR-008 ..."
```

#### Caso 3: Añades nuevo proceso ETL
```
Editas: knowledge_base/Data/ETL Processes.md
       → Documentas el nuevo proceso
Editas: knowledge_base/Development/Commands.md
       → Añades el comando
Commit: git add . && git commit -m "docs: Add new ETL XYZ"
```

---

## 🤖 Para Claude Code

### Al Inicio de Sesión

1. **Lee CLAUDE.md** (auto-generado, siempre fresco)
2. **Lee MEMORY.md** que ahora prioriza `project_obsidian_knowledge_base.md`
3. **Cuando necesite contexto adicional**, consulta directamente `knowledge_base/`

### Patrones de Consulta

#### Pregunta del usuario → Archivo a consultar

| Pregunta | Archivo |
|----------|---------|
| "¿Cómo está X ahora?" | `Project Root/STATUS.md` |
| "¿Cómo arranco X?" | `Development/Commands.md` |
| "¿Por qué hicimos Y?" | `Architecture/Decisions Log.md` |
| "¿Cuál es la paleta?" | `Brand/Visual Identity.md` |
| "¿Cómo funciona el ETL?" | `Data/ETL Processes.md` |
| "Error: X no funciona" | `Development/Debugging Guide.md` |
| "¿Cómo va el cron?" | `Workflows/Daily Automation.md` |
| "¿Qué cambió últimamente?" | `Project Root/CHANGELOG.md` |

---

## 🔧 Setup Obsidian (Una Vez)

### Si nunca has abierto Obsidian
1. Descargar: https://obsidian.md/
2. Abrir Obsidian
3. "Open folder as vault" → `C:\Users\rover\dosaros-data-project\knowledge_base\`
4. Ya está. Verás `INDEX.md` como dashboard

### Plugins Recomendados
- **Dataview** — Queries dinámicos sobre notas
- **Templater** — Plantillas para nuevas notas
- **Excalidraw** — Diagramas embebidos
- **Obsidian Git** — Auto-sync con repo

### Configuración del Vault
- ✅ Strict line breaks: OFF (mejor para markdown)
- ✅ Show inline title: ON
- ✅ Use [[Wikilinks]]: ON
- ✅ Default location for new attachments: `Templates/attachments/`

---

## 📋 Cheat Sheet

### Comandos Esenciales

```bash
# Arrancar dev server
npm run dev

# Sincronizar Obsidian → CLAUDE.md (manual)
python scripts/sync_obsidian_to_claude.py

# Verificar qué cambiaría sin escribir
python scripts/sync_obsidian_to_claude.py --dry-run

# Backup actual de CLAUDE.md
cat CLAUDE.md.bak  # se crea automáticamente

# Workflow GitHub
git add knowledge_base/
git commit -m "docs: ..."
git push origin main
# → GitHub Action regenera CLAUDE.md automáticamente
```

### Estructura de Carpetas a Recordar

```
knowledge_base/
├── INDEX.md                  ← Empieza aquí
├── Project Root/             ← Overview, STATUS, CHANGELOG
├── Architecture/             ← Diseño, ADRs
├── Brand/                    ← Visual identity
├── Data/                     ← Schema, ETL
├── Development/              ← Setup, comandos, debug
├── Workflows/                ← Cron, automatización
├── NBA/ EuroLeague/          ← Reference
├── Insights/                 ← Resultados
└── Templates/                ← Plantillas
```

---

## ✅ Checklist Post-Setup

- [ ] Obsidian abierto en `knowledge_base/`
- [ ] `INDEX.md` accesible como dashboard
- [ ] Script de sync funciona: `python scripts/sync_obsidian_to_claude.py --dry-run`
- [ ] GitHub Action visible: `https://github.com/dosaroscontact/dosaros-data-project/actions`
- [ ] `CLAUDE.md` tiene header "AUTO-GENERADO desde Obsidian"
- [ ] Claude Code memory referencia Obsidian (`project_obsidian_knowledge_base.md`)

---

## 🔗 Links Importantes

- [[README|📖 Overview del proyecto]]
- [[STATUS|📊 Estado actual]]
- [[../Development/Environment Setup|💻 Setup entornos]]
- [[../Workflows/Sync Obsidian to Claude|🔁 Detalles del sync]]
- [[../Architecture/Decisions Log|📝 ADRs]]

---

## 🆘 Si Algo Va Mal

### CLAUDE.md tiene contenido incorrecto
```bash
# 1. Restaurar backup
cp CLAUDE.md.bak CLAUDE.md

# 2. Identificar problema en Obsidian
# 3. Editar archivo fuente
# 4. Re-ejecutar sync
python scripts/sync_obsidian_to_claude.py
```

### GitHub Action falla
1. Ver: https://github.com/dosaroscontact/dosaros-data-project/actions
2. Click en el job que falló
3. Ver logs del paso "Run sync script"
4. Generalmente: error de encoding o sintaxis Python

### Obsidian no muestra links bidireccionales
- Settings → Files & Links → Use [[Wikilinks]] = ON
- Settings → Files & Links → New link format = "Shortest path when possible"

---

**Última actualización**: 2026-05-17
**Versión del sistema**: 1.0 (post-migración Obsidian)
