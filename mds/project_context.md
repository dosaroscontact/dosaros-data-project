# DOS AROS

## Documento Base de Estrategia, Arquitectura y Metodología

**Versión 1.0 — Documento Fundacional**

---

# 1. Naturaleza del Proyecto

## 1.1 Definición

**Dos Aros** es un sistema de investigación aplicada al baloncesto comparado entre NBA y EuroLeague, complementado por una capa editorial que publica los resultados derivados de esa investigación.

El proyecto no nace como un medio, ni como un producto tecnológico, sino como:

> Un laboratorio personal de análisis cuantitativo del juego.

La publicación es una consecuencia, no el objetivo inicial.

---

## 1.2 Filosofía Central

El principio rector del proyecto es:

> **Datos primero. Contexto después. Opinión al final.**

Esto implica:

* No se parte de narrativas.
* No se buscan conclusiones predeterminadas.
* No se comenta actualidad.
* No se reacciona a partidos concretos.
* Se investigan patrones estructurales.

---

## 1.3 Objetivo Real

Construir, con el tiempo, un archivo analítico coherente que permita responder preguntas como:

* ¿Cómo evoluciona el juego cuando cambian las reglas?
* ¿Qué diferencias son culturales y cuáles estructurales?
* ¿Qué métricas sobreviven al cambio de contexto competitivo?
* ¿Cómo se ajusta el rendimiento en playoffs frente a temporada regular?

---

# 2. Estructura del Proyecto: Dos Líneas Conectadas

## 2.1 Línea 1 — Sistema de Investigación (Core)

Es la base real del proyecto.

Funciona como:

* Entorno de análisis personal.
* Sistema de almacenamiento incremental de datos.
* Plataforma para formular y testear hipótesis.
* Laboratorio cuantitativo.

No está diseñado para ser público.

---

## 2.2 Línea 2 — Capa Editorial

Es la traducción del trabajo interno a contenido comprensible.

Publica:

* Hilos analíticos.
* Artículos extensos.
* Explicaciones metodológicas.
* Resultados seleccionados.

Nunca expone la base de datos completa.

---

## 2.3 Evolución Prevista

A medio plazo podrá abrirse parcialmente el sistema mediante:

* Consultas en lenguaje natural.
* Acceso a conocimiento derivado.
* Interacción guiada, no acceso bruto al dato.

---

# 3. Alcance Inicial del Proyecto

## 3.1 Plataformas Activas (Fase 1)

Solo se utilizarán:

* X → Publicación breve analítica.
* Newsletter → Desarrollo en profundidad.

No se usará:

* Instagram
* TikTok
* Vídeo
* Otras redes

El objetivo es evitar dispersión.

---

# 4. Arquitectura Técnica General

El sistema sigue un enfoque **local-first con publicación selectiva**.

---

## 4.1 Jerarquía de Datos

### Base Principal (Data Warehouse Real)

**SQLite en Raspberry Pi**

Contiene:

* Histórico completo.
* Datos pesados.
* Tablas extensas.
* Dataset vivo de investigación.

Es la fuente real de verdad.

---

### Base Secundaria (Serving Layer)

**Supabase PostgreSQL**

Contiene solo:

* Datos agregados.
* Resultados procesados.
* Información necesaria para visualización.

Su función es servir, no almacenar.

---

## 4.2 Flujo de Datos

Extracción → SQLite (almacenamiento total)
Transformación → Procesamiento analítico
Selección → Subconjunto optimizado
Carga → Supabase
Consumo → Visualización o publicación

---

## 4.3 Automatización

GitHub actúa como:

* Orquestador de tareas.
* Control de versiones.
* Ejecutor programado de ETL.

---

## 4.4 Rol del Portátil

El portátil es:

* Entorno de desarrollo.
* Lugar donde se diseñan análisis.
* No almacena datos críticos.

---

# 5. Filosofía de Ingestión de Datos

## 5.1 Modelo Incremental

El sistema crece según necesidad analítica.

No existe una carga histórica masiva inicial.

---

## 5.2 Backfill Bajo Demanda

Si se necesita una temporada no existente:

* Se descarga únicamente ese bloque.
* Se integra en SQLite.
* Pasa a formar parte del archivo.

---

## 5.3 Resultado

La base de datos es:

> Un archivo orgánico guiado por preguntas, no por disponibilidad.

---

# 6. Metodología de Investigación

Cada análisis sigue una estructura obligatoria:

1. Pregunta clara.
2. Definición de variables.
3. Extracción de datos necesarios.
4. Normalización.
5. Análisis.
6. Resultado.
7. Interpretación mínima.

---

## 6.1 Principio Fundamental

Nunca analizar métricas sin contexto de posesiones.

Ejemplo:

PPG = función de Pace y Offensive Rating
No es una medida independiente.

---

# 7. Visualización

## 7.1 Librería Oficial

Matplotlib es el estándar único.

Motivos:

* Reproducibilidad.
* Control absoluto.
* Estética analítica.
* Estabilidad.

---

## 7.2 Estilo Visual

* Fondo blanco.
* Gráficos tipo paper técnico.
* Sin estética de dashboard.
* Claridad antes que diseño.

---

## 7.3 Colores

NBA → Azul #1f77b4
EuroLeague → Naranja #ff7f0e

---

# 8. Uso de Inteligencia Artificial Local

El sistema integra modelos locales mediante Ollama para:

* Consultas en lenguaje natural sobre la base SQLite.
* Exploración rápida de hipótesis.
* Traducción de preguntas humanas a queries.

La IA no genera contenido final.
Es una herramienta de trabajo.

---

# 9. Caso Funcional Inicial (Caso 0)

## Investigación:

Diferencia entre Regular Season y Playoffs a lo largo del tiempo.

Objetivo:

Determinar si la caída de anotación responde a:

* Menor ritmo
* Mayor defensa
* Ajustes tácticos
* Cambios de era

Este caso valida todo el ecosistema:

* Ingestión dirigida
* Modelado incremental
* Visualización reproducible
* Publicación derivada

---

# 10. Política de Idioma

Idioma principal: Español.

Terminología técnica: Se mantiene en inglés cuando sea estándar.

Ejemplo:

pace
offensive rating
sample
query
dataset

Evita traducciones artificiales.

---

# 11. Restricciones Legales y Editoriales

El proyecto:

* No utiliza logos oficiales.
* No utiliza fotografías protegidas.
* No redistribuye bases de datos completas.
* Publica solo resultados analíticos propios.

---

# 12. Qué NO Es Dos Aros

No es:

* Un medio de actualidad.
* Una cuenta de opinión.
* Un dashboard público masivo.
* Un SaaS de estadísticas.
* Un agregador de datos.

---

# 13. Qué Es Dos Aros

Es:

> Un laboratorio personal de investigación sobre baloncesto que publica conocimiento cuando merece ser publicado.

---

# 14. Principio de Sostenibilidad

El proyecto debe poder mantenerse durante años con:

* Bajo coste.
* Bajo mantenimiento.
* Alta curiosidad intelectual.

Si una decisión aumenta la complejidad sin aumentar la capacidad de responder preguntas, se descarta.

---

**Fin del Documento Fundacional**
# DOS AROS

## Documento Base de Estrategia, Arquitectura y Estado Actual

**Versión 1.1 — Documento Fundacional Vivo**

---

# 1. Naturaleza del Proyecto

**Dos Aros** es un sistema de investigación aplicada al baloncesto comparado (NBA / EuroLeague) construido como laboratorio personal de análisis cuantitativo, con una capa editorial posterior.

No es un medio.
No es un producto de datos.
Es un entorno de investigación que eventualmente publica conocimiento.

Principio rector:

> Datos → Modelo → Comprensión → Publicación (solo si aporta valor)

---

# 2. Alcance del Proyecto

El proyecto tiene **dos líneas simultáneas**:

## 2.1 Línea Interna (Principal)

Sistema diseñado para:

* Investigar.
* Formular hipótesis.
* Construir datasets propios.
* Generar análisis que sirvan como base para publicaciones.

## 2.2 Línea Pública (Derivada)

Publicación de resultados en:

* **X (Twitter)** → formato corto.
* **Newsletter** → formato largo.

No se usará ninguna otra plataforma en fase inicial.

---

# 3. Filosofía de Datos

## 3.1 Modelo Incremental Bajo Demanda

No existe una ingesta histórica masiva.

El sistema solo descarga datos cuando:

* Son necesarios para un análisis.
* Un usuario solicita una temporada no existente.
* Se amplía el archivo de investigación.

Ejemplo:

* Si 2026 ya existe → actualización incremental.
* Si alguien pide 2004 → se construye ese bloque en ese momento.

La base crece guiada por preguntas, no por disponibilidad.

---

# 4. Arquitectura Técnica

## 4.1 Base de Datos Principal (Repositorio Real)

**SQLite en Raspberry Pi**

Funciona como:

* Data Warehouse completo.
* Archivo histórico.
* Entorno de trabajo pesado.
* Copia persistente sin costes cloud.

Aquí vive **la base grande**.

---

## 4.2 Base de Datos de Servicio

**Supabase (PostgreSQL)**

Contiene solo:

* Datos agregados.
* Subconjuntos preparados.
* Información necesaria para visualización o publicación.

Su función es servir datos, no almacenarlos masivamente.

Esto evita:

* Aumento de costes.
* Dependencia cloud innecesaria.

---

## 4.3 Orquestación

El repositorio Git actúa como:

* Fuente de verdad del código.
* Sistema de automatización.
* Coordinador de ETL.

---

## 4.4 Entorno Local (Portátil)

Se usa exclusivamente para:

* Desarrollo.
* Pruebas.
* Diseño analítico.

No es infraestructura.

---

# 5. Uso de IA Local

Se utiliza **Ollama en local** para:

* Consultas en lenguaje natural contra la base SQLite.
* Exploración rápida de hipótesis.
* Asistencia analítica.

La IA:

* No publica.
* No decide.
* No sustituye el análisis.

Es una herramienta de trabajo.

---

# 6. Visualización

Se usará exclusivamente:

**Matplotlib**

Motivos:

* Control total.
* Reproducibilidad.
* Estética técnica (no dashboard).
* Adecuado para publicación analítica.

Estilo:

* Fondo blanco.
* Sin elementos decorativos.
* Gráficos tipo paper.

---

# 7. Política de Idioma

Idioma base: Español.

Terminología técnica permanece en inglés cuando es estándar:

* pace
* offensive rating
* dataset
* query
* sample

Se evita traducción artificial.

---

# 8. Estado Actual del Repositorio (Implementación Real)

Actualmente el proyecto **ya tiene estructura funcional creada**.
Lo siguiente documenta exactamente lo existente.

---

## 8.1 Estructura de Directorios

```
project/
│
├── project_context.md
├── README.md
├── requirements.txt
├── task.md
│
└── src/
    ├── __init__.py
    │
    ├── app/
    │   ├── analista_ia.py
    │   ├── chat_boloncesto.py
    │   ├── consulta_ia.py
    │   ├── inicializar_db.py
    │   ├── init_local_db.py
    │   ├── main.py
    │   └── components/
    │
    ├── database/
    │   ├── __init__.py
    │   └── supabase_client.py
    │
    └── etl/
        ├── __init__.py
        ├── historical_games.py
        ├── local_nba_sync.py
        ├── nba_extractor.py
        ├── nba_games_extractor.py
        └── nba_player_extractor.py
```

Los directorios `__pycache__` existen como artefactos automáticos de Python y no forman parte del diseño lógico.

---

## 8.2 Archivos Raíz

### `project_context.md`

Documento interno de notas y contexto del proyecto.

### `README.md`

Explicación general, objetivos y forma de ejecución.

### `requirements.txt`

Dependencias Python necesarias para reproducir el entorno.

### `task.md`

Listado de tareas y roadmap operativo.

---

# 9. Módulo `src/app` — Capa de Interacción y Análisis

Contiene la lógica orientada a uso analítico e interacción.

### `analista_ia.py`

Funciones de análisis asistido por IA para procesar consultas y generar interpretaciones.

### `chat_boloncesto.py`

Gestión del flujo conversacional específico del dominio baloncesto.

### `consulta_ia.py`

Utilidades para:

* Construcción de prompts.
* Formateo de consultas.
* Comunicación con modelos IA.

### `inicializar_db.py`

Preparación de la base de datos remota:

* Creación de estructuras.
* Inicialización necesaria en Supabase.

### `init_local_db.py`

Inicialización de la base local SQLite:

* Creación de esquema.
* Seeds iniciales.

### `main.py`

Punto de entrada de la aplicación.

### `components/`

Componentes reutilizables de interfaz (pensados para Streamlit u otra UI ligera).

---

# 10. Módulo `src/database` — Acceso a Datos Remotos

### `supabase_client.py`

Wrapper de conexión con Supabase:

* Conexión autenticada.
* Operaciones CRUD.
* Abstracción de queries.

---

# 11. Módulo `src/etl` — Pipeline de Ingesta

Es el núcleo del sistema de construcción de datos.

### `historical_games.py`

Carga y procesamiento de partidos históricos.

### `local_nba_sync.py`

Sincronización local periódica:
Actúa como orquestador del ETL en entorno local.

### `nba_extractor.py`

Extractor base de datos NBA desde fuente externa.

### `nba_games_extractor.py`

Extracción específica de información de partidos:

* Scores
* Fechas
* Identificadores

### `nba_player_extractor.py`

Extracción específica de jugadores:

* Estadísticas
* Identidades
* Relaciones jugador-temporada

---

# 12. Flujo Operativo Real

El flujo actual del sistema es:

1. Se necesita un análisis.
2. Se ejecuta ETL dirigido desde `src/etl`.
3. Los datos se almacenan en SQLite local.
4. Se analizan mediante scripts + IA local.
5. Si algo debe exponerse → se replica subconjunto a Supabase.
6. Se publica contenido derivado.

---

# 13. Principio de Diseño que Rige Todo

> El sistema está diseñado para responder preguntas, no para acumular datos.

Si una pieza no ayuda a responder mejor una pregunta analítica, no se añade.

---

**Fin del Documento (v1.1 — Estado Actual Documentado)**
