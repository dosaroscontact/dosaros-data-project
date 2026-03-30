# 📚 Índice Maestro - Documentación Dos Aros para Claude Code

**Guía rápida: cuál documento leer según tu necesidad.**

---

## 🎯 ELIGE TU RUTA

### "Acabo de empezar, ¿por dónde inicio?"
→ Lee en este orden:
1. **CLAUDE_CODE_CONTEXT.md** (entender el proyecto)
2. **PROJECT_STRUCTURE.md** (ver la estructura)
3. **BOT_MANUAL.md** (cómo funciona el bot)

### "Necesito hacer un cambio en el código"
→ Lee en este orden:
1. **QUICK_REFERENCE.md** (comandos rápidos)
2. **DEVELOPMENT_GUIDE.md** (flujo de cambio)
3. **DATABASE_SCHEMA.md** (si afecta BBDD)

### "El bot está roto, necesito debugging"
→ Lee en este orden:
1. **QUICK_REFERENCE.md** (seción "Debugging Común")
2. **CLAUDE_CODE_CONTEXT.md** (seción "Problemas Comunes")
3. **DATABASE_SCHEMA.md** (si es error de BBDD)

### "Voy a generar avatares y publicarlos"
→ Lee en este orden:
1. **BOT_MANUAL.md** (guías prácticas)
2. **AVATAR_SYSTEM_DOCS.md** (arquitectura completa)

---

## 📖 LISTA COMPLETA DE DOCUMENTOS

### 1. **CLAUDE_CODE_CONTEXT.md** ⭐ EMPIEZA AQUÍ
**Propósito:** Entender la arquitectura general del proyecto

**Contiene:**
- Ubicación del proyecto (Windows, Pi, GitHub)
- Arquitectura general (flujo de datos)
- Componentes principales (BBDD, Bot, Scripts)
- Variables críticas (.env, rutas)
- Flujos principales (3 flujos clave)
- Tecnologías usadas
- Scripts principales
- Problemas comunes

**Cuándo leer:**
- Primer día trabajando con el proyecto
- Cuando necesitas entender cómo funciona todo

**Tiempo:** 10 minutos

---

### 2. **PROJECT_STRUCTURE.md**
**Propósito:** Conocer la estructura de carpetas y archivos

**Contiene:**
- Árbol completo del proyecto
- Relaciones de archivos clave
- Archivos críticos (no eliminar)
- Archivos editables seguros
- Localizaciones importantes (Windows, Pi, GitHub)
- Flujo de cambios
- Dependencias principales
- Puntos de entrada

**Cuándo leer:**
- Cuando necesitas navegar el proyecto
- Cuando creas nuevos archivos
- Para entender dónde va cada cosa

**Tiempo:** 5 minutos

---

### 3. **QUICK_REFERENCE.md** ⭐ MÁS USADO
**Propósito:** Comandos rápidos que copiar/pegar

**Contiene:**
- Comandos críticos (iniciar/detener bot)
- Comandos BBDD (queries útiles)
- Comandos Git (commit, push, pull)
- Comandos Telegram (para testear)
- Variables de entorno
- Cambios de directorio frecuentes
- Debugging común
- Snippets SQL frecuentes
- Patrones comunes
- Monitoreo diario
- Emergencias (qué hacer si todo falla)

**Cuándo usar:**
- Cuando necesitas ejecutar algo específico en Pi
- Cuando necesitas una query SQL
- Cuando debugueas

**Tiempo:** 1 minuto (lookup)

---

### 4. **DEVELOPMENT_GUIDE.md** ⭐ PARA CAMBIOS
**Propósito:** Cómo hacer cambios de forma segura

**Contiene:**
- Checklist pre-cambio
- Flujo estándar de desarrollo (6 pasos)
- Patrones de edición comunes (5 patrones)
- Cambios críticos y cómo hacerlos
- Código de calidad (checklist + template)
- Testing (3 niveles, template)
- Documentación (cuándo actualizar)
- Despliegue a producción
- Rollback de emergencia
- Comunicación con Robe (formato)

**Cuándo leer:**
- Antes de hacer cualquier cambio en código
- Cuando necesitas entender best practices
- Cuando cambias algo crítico (bot, BBDD, cron)

**Tiempo:** 15 minutos

---

### 5. **DATABASE_SCHEMA.md** ⭐ PARA BBDD
**Propósito:** Documentación completa de la BBDD

**Contiene:**
- Ubicación del archivo BBDD
- Esquema de 3 tablas (DDL completo)
- Descripción de cada columna con ejemplos
- Scene types explicados
- Ejemplos de registros reales
- Relaciones entre tablas
- Estadísticas (counts)
- 7 queries útiles
- Operaciones comunes (insert, update, delete)
- Mantenimiento (backup, verificación)
- Notas importantes
- Seguridad (SQL injection prevention)

**Cuándo leer:**
- Cuando trabajas con datos de BBDD
- Cuando escribes queries SQL
- Cuando cambias estructura de BBDD
- Cuando necesitas entender las tablas

**Tiempo:** 10 minutos

---

### 6. **BOT_MANUAL.md**
**Propósito:** Guía de uso del bot para usuarios

**Contiene:**
- Introducción al bot
- 5 comandos disponibles explicados
- 3 guías paso a paso (avatar, consultas, video)
- 3 flujos de trabajo
- 3 ejemplos prácticos completos
- Troubleshooting (7 problemas comunes)
- Contact/Soporte
- Cheat sheet

**Cuándo usar:**
- Para entender cómo funciona el bot
- Cuando necesitas ejemplos de cómo usarlo
- Para resolver problemas de usuario
- Para documentar nuevos comandos

**Tiempo:** 20 minutos para lectura completa

---

### 7. **AVATAR_SYSTEM_DOCS.md**
**Propósito:** Documentación técnica completa del sistema avatar

**Contiene:**
- Contexto del proyecto
- Estado actual (BBDD, scripts, estado)
- Estructura GitHub
- URLs confirmadas (avatares + logos)
- Scripts principales (5 scripts)
- Template de prompt completo
- Flujo de generación (3 pasos)
- Estadísticas actuales
- Próximos pasos (4 fases)
- Troubleshooting (3 problemas)
- Referencias

**Cuándo leer:**
- Para entender todo sobre avatares
- Cuando debugueas problemas de prompts
- Para entender el flujo completo

**Tiempo:** 25 minutos

---

## 🗺️ MATRIZ DE REFERENCIA RÁPIDA

| Necesidad | Documento | Sección |
|-----------|-----------|---------|
| Entender proyecto | CLAUDE_CODE_CONTEXT | Introducción |
| Estructura carpetas | PROJECT_STRUCTURE | Árbol completo |
| Comando para X | QUICK_REFERENCE | Buscar en lista |
| Hacer cambio en código | DEVELOPMENT_GUIDE | Flujo estándar |
| Query SQL | DATABASE_SCHEMA | Queries útiles |
| Query SQL | QUICK_REFERENCE | Snippets SQL |
| Usar comando bot | BOT_MANUAL | Comandos disponibles |
| Ejemplo práctico | BOT_MANUAL | Ejemplos prácticos |
| Avatar detail | AVATAR_SYSTEM_DOCS | Documentación completa |
| Debugging bot | QUICK_REFERENCE | Debugging común |
| Debugging bot | CLAUDE_CODE_CONTEXT | Problemas comunes |
| Problema BBDD | DATABASE_SCHEMA | Mantenimiento |
| Problema cron | QUICK_REFERENCE | Emergencias |
| Ver estructura BBDD | DATABASE_SCHEMA | Tablas principales |
| Best practices | DEVELOPMENT_GUIDE | Código de calidad |

---

## 🚀 WORKFLOWS COMUNES

### Workflow 1: "Quiero agregar un nuevo comando al bot"

```
1. Leer: DEVELOPMENT_GUIDE (Flujo estándar)
2. Editar: src/automation/bot_consultas.py
3. Consultar: QUICK_REFERENCE (Git commands)
4. Push a GitHub
5. Pull en Pi
6. Referencia: QUICK_REFERENCE (Reiniciar bot)
7. Test en Telegram
```

### Workflow 2: "Necesito debuguear por qué el bot no responde"

```
1. Ver: QUICK_REFERENCE (Debugging común)
2. Ejecutar: Comandos de verificación
3. Si falla BBDD: DATABASE_SCHEMA
4. Si falla token: CLAUDE_CODE_CONTEXT
5. Si falla cron: QUICK_REFERENCE (Emergencias)
```

### Workflow 3: "Voy a generar avatares hoy"

```
1. Leer: BOT_MANUAL (Avatar Commands)
2. Telegram: /avatar_today
3. Leer: BOT_MANUAL (Guía 2: Avatar Aleatorio)
4. Abrirt: Google ImageFX
5. Publicar en redes
```

### Workflow 4: "Necesito una query SQL específica"

```
1. Buscar en: DATABASE_SCHEMA (Queries útiles)
2. Si no está: DATABASE_SCHEMA (Patrones)
3. Si necesito: QUICK_REFERENCE (Snippets SQL)
4. Ejecutar: sqlite3 /mnt/nba_data/dosaros_local.db "SELECT..."
```

---

## 📊 ESTADÍSTICAS DE LOS DOCUMENTOS

| Documento | Tamaño | Duración lectura | Palabras |
|-----------|--------|-----------------|----------|
| CLAUDE_CODE_CONTEXT | 8 KB | 10 min | ~2,000 |
| PROJECT_STRUCTURE | 7 KB | 5 min | ~1,800 |
| QUICK_REFERENCE | 12 KB | 1 min | ~3,500 |
| DEVELOPMENT_GUIDE | 14 KB | 15 min | ~3,800 |
| DATABASE_SCHEMA | 11 KB | 10 min | ~3,000 |
| BOT_MANUAL | 18 KB | 20 min | ~4,500 |
| AVATAR_SYSTEM_DOCS | 16 KB | 25 min | ~4,200 |
| **TOTAL** | **86 KB** | **86 min** | **~23,000** |

---

## 🎯 PARA CLAUDE CODE ESPECÍFICAMENTE

### Qué hacer cuando Robe pide algo:

**Opción 1: Cambio en código**
```
1. Leer DEVELOPMENT_GUIDE (todo el flujo)
2. Clonar repo (si no existe)
3. Hacer cambios en archivo
4. Leer QUICK_REFERENCE (git commands)
5. Commit y push
6. Informar a Robe que en Pi hay que hacer git pull
```

**Opción 2: Query o debugging**
```
1. Buscar en QUICK_REFERENCE o DATABASE_SCHEMA
2. Proporcionar comando/query a Robe
3. Robe lo ejecuta en Pi
4. Robe devuelve output
5. Yo (Claude Code) analizo resultado
```

**Opción 3: Explicar algo**
```
1. Consultar el documento relevante
2. Dar explicación clara
3. Incluir ejemplos de referencia
4. Ofrecer próximos pasos
```

---

## ✅ CHECKLIST: Documentación Instalada

- [x] CLAUDE_CODE_CONTEXT.md (Contexto general)
- [x] PROJECT_STRUCTURE.md (Estructura de carpetas)
- [x] QUICK_REFERENCE.md (Comandos rápidos)
- [x] DEVELOPMENT_GUIDE.md (Guía de desarrollo)
- [x] DATABASE_SCHEMA.md (Esquema BBDD)
- [x] BOT_MANUAL.md (Manual del bot)
- [x] AVATAR_SYSTEM_DOCS.md (Docs de avatares)
- [x] Este índice (INDEX_MASTER.md)

**Total:** 8 documentos = ~86 KB = ~23,000 palabras

---

## 🔗 CÓMO AÑADIR A CLAUDE CODE

### Opción 1: Copiar directamente en chat
```
Copia el contenido del documento y pégalo en el chat de Claude Code
con el tema específico
```

### Opción 2: Referenciar en GitHub
```
"Ve al repo en GitHub y mira estos documentos:
- docs/CLAUDE_CODE_CONTEXT.md
- docs/DEVELOPMENT_GUIDE.md
- etc"
```

### Opción 3: Incluir en system prompt
```
Si usas Claude Code como API, agregar estos docs al system prompt
para que siempre tenga contexto
```

---

## 📞 SOPORTE

**¿Documento incompleto o confuso?**
→ Informar a Robe con:
- Qué documento
- Qué sección
- Qué información falta
- Sugerencia de mejora

**¿Cambios en el proyecto?**
→ Actualizar documento correspondiente:
- Nuevo script → QUICK_REFERENCE + DEVELOPMENT_GUIDE
- Cambio BBDD → DATABASE_SCHEMA
- Nuevo comando → BOT_MANUAL + QUICK_REFERENCE
- Cambio arquitectura → CLAUDE_CODE_CONTEXT

---

**Versión:** 1.0  
**Fecha:** 2026-03-29  
**Estado:** ✅ COMPLETO Y LISTO PARA USAR

---

## 🎓 CÓMO USAR ESTA DOCUMENTACIÓN

1. **Primera vez:** Lee CLAUDE_CODE_CONTEXT.md completo (10 min)
2. **Cada cambio:** Consulta DEVELOPMENT_GUIDE.md (según el cambio)
3. **Debugging:** QUICK_REFERENCE.md (búsqueda rápida)
4. **BBDD:** DATABASE_SCHEMA.md (cuando necesites)
5. **Dudas bot:** BOT_MANUAL.md (ejemplos completos)

**Objetivo:** Que tengas toda la información necesaria sin depender de Robe para cada pregunta.

¡Listo para trabajar con Claude Code! 🚀
