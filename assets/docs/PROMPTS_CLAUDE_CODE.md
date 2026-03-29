# 💬 PROMPTS PARA CLAUDE CODE

Usa estos prompts en claude.ai/code para mejorar y personalizar tu integración.

---

## PROMPT 1: Verificar Instalación Completa

```
/start

Quiero verificar que mi integración de Editor Pro Max con Dos Aros está 
completamente instalada y funcionando.

Estos son mis archivos principales:
- src/integrations/video_generator/video_generator.py
- src/integrations/telegram_video_handler.py
- src/integrations/__init__.py
- editor_pro_max/ (la carpeta clonada)

¿Puedes:
1. Verificar que los imports están correctos
2. Testear que VideoGenerator se carga sin errores
3. Verificar conexión con SQLite
4. Verificar que las APIs están configuradas
5. Crear un script de test que verifique todo esto
```

---

## PROMPT 2: Mejorar Manejo de Errores

```
Quiero mejorar el manejo de errores en video_generator.py.

Necesito:
1. Retry automático si Remotion falla (máximo 3 intentos)
2. Fallback a Claude si Gemini no responde
3. Validación de composición antes de renderizar
4. Timeout inteligente según duracion del video
5. Logs detallados en archivo

Los errores más comunes son:
- Remotion timeout (>10min)
- API rate limits
- BD connection issues
- Composición TSX inválida

¿Puedes crear una versión mejorada con estos controles?
```

---

## PROMPT 3: Caché de Composiciones

```
Quiero evitar regenerar composiciones idénticas.

Necesito un sistema de caché que:
1. Genere hash de la instrucción + contexto
2. Almacene composiciones en src/compositions/.cache
3. Reutilice si encuentra hash idéntico
4. Tenga TTL de 24 horas
5. Permita limpiar caché con comando /vclear

¿Puedes integrar esto en VideoGenerator?
```

---

## PROMPT 4: Monitor de Recursos

```
Quiero un sistema que monitoree:
1. Uso de CPU durante renderizado
2. Uso de RAM
3. Espacio en disco disponible
4. Tiempo promedio de renderizado
5. Éxito/fallo rate

Necesito:
- Archivo de logs con métricas
- Comando /vstats que muestre las métricas
- Alerta si CPU > 80% o RAM > 90%
- Auto-stop si disco < 1GB

¿Puedes crear VideoMonitor?
```

---

## PROMPT 5: Cola de Renderizado

```
Actualmente genera videos secuencialmente.

Necesito una cola que:
1. Permita pedir hasta 5 videos simultáneamente
2. Procese en paralelo (max 2 renderizaciones paralelas)
3. Notifique progreso en Telegram
4. Guarde historial de jobs
5. Permita pausar/reanudar con /vpause, /vresume

¿Puedes crear VideoRenderQueue?
```

---

## PROMPT 6: Mejorar Prompts de Claude

```
Los prompts que Claude recibe para generar composiciones a veces generan 
código que no compila. 

Necesito mejorar:
1. Ser más explícito sobre imports permitidos
2. Incluir ejemplos de código válido
3. Validar TypeScript antes de renderizar
4. Si hay error, pedir a Claude que lo corrija
5. Mantener registro de prompts que funcionan vs no

¿Puedes reescribir _generar_prompt_claude() para que sea más robusto?
```

---

## PROMPT 7: Presets de Videos Personalizados

```
Quiero crear presets predefinidos para casos comunes:

1. BREAKING: Resultado de partido (30s)
2. STATS: Top 3 de la semana (45s)  
3. COMPARISON: NBA vs Euro (60s)
4. ANALYSIS: Análisis profundo (90s)
5. HILO: Múltiples videos para thread (5 x 15s)

Cada preset tiene:
- Template automático
- Colores predefinidos
- Duración fija
- Estructura de composición

¿Puedes crear un sistema de presets?

Ejemplo uso:
/video --preset breaking Celtics vs Lakers final
/video --preset stats top 3 tiradores esta semana
```

---

## PROMPT 8: Integración con Base de Datos Avanzada

```
Mi SQLite tiene estos datos:
- nba_stats: player_name, team_abbreviation, pts, 3p, ast, reb, game_date
- euro_stats: player_name, team_code, Points, Assists, TotalRebounds, Minutes, game_date
- games: game_date, home_team, away_team, home_score, away_score
- players: player_id, player_name, height, weight, position

Necesito consultas más inteligentes que:
1. Detecten si es pregunta sobre NBA o Euro automáticamente
2. Busquen por jugador, equipo, estadística
3. Agreguen datos (promedios, máximos, mínimos)
4. Manejen comparativas NBA vs Euro
5. Cacheen resultados frecuentes

¿Puedes crear un QueryBuilder más inteligente?
```

---

## PROMPT 9: Generador de Paleta de Colores Dinámicos

```
Actualmente uso colores hardcodeados (#88D4AB, #FF8787).

Quiero que genere paletas dinámicamente basadas en:
1. Equipo (usar colores oficiales NBA/Euro)
2. Contraste automático para legibilidad
3. Tema (oscuro/claro)
4. Número de variables: 3-5 colores coordinados

Necesito:
- Diccionario de colores oficiales de todos los equipos
- Función que genere paleta coherente
- Validar contraste WCAG AA mínimo

¿Puedes crear ColorPaletteGenerator?

Ejemplo:
- Instrucción: "Lakers"
- Auto-detectar: Purple (#552583), Gold (#FDB827)
- Generar paleta completa con esos colores base
```

---

## PROMPT 10: Testing y Validación

```
Necesito un suite de tests para video_generator.py:

1. Test de imports (VideoGenerator, APIManager, DB)
2. Test de extracción de contexto (diferentes instrucciones)
3. Test de consultas a BD (verificar estructura datos)
4. Test de generación de prompt (validar que es válido)
5. Test de generación de código (validar TypeScript)
6. Test de renderizado (mock de Remotion)
7. Test de manejo de errores (diferentes fallos)
8. Test de rendimiento (timeout checks)

¿Puedes crear test_video_generator.py completo con pytest?
```

---

## PROMPT 11: Dashboard Admin en Telegram

```
Quiero un dashboard en Telegram que muestre:

1. Videos generados (últimos 10)
2. Estadísticas de uso (usuarios, videos, tiempo promedio)
3. Uso de recursos (CPU, RAM, disco)
4. APIs status
5. Composiciones en caché (tamaño, últimos accesos)
6. Órdenes en cola

Comando: /vdash

¿Puedes crear un DatabaseManager que recopile estas métricas?
```

---

## PROMPT 12: Exportar a Múltiples Formatos

```
Actualmente exporto solo MP4.

Necesito poder exportar a:
1. MP4 (actual)
2. WebM (calidad web)
3. GIF (para Twitter)
4. HLS (para streaming)
5. Vertical (móvil) y horizontal (desktop)

Con comandos como:
/video "instrucción" --format webm
/video "instrucción" --all (genera todos)

¿Puedes extender VideoGenerator con MultiFormatExporter?
```

---

## PROMPT 13: Análisis de Composición Generada

```
Antes de renderizar, quiero validar que la composición es válida.

Necesito un validator que compruebe:
1. TypeScript válido (sin errores de sintaxis)
2. Todos los imports existen
3. La composición exporta el nombre correcto
4. No usa packages prohibidos
5. Las dimensiones son válidas (1080/1920)
6. La duración está dentro de límites (15-90s)
7. No tiene console.log en versión final

Si hay error:
1. Mostrar el error específico
2. Pedir a Claude que lo corrija
3. Reintentar hasta 3 veces
4. Si sigue fallando, usar template fallback

¿Puedes crear CompositionValidator?
```

---

## PROMPT 14: Integración con Otras APIs Externas

```
Quiero integrar con:
1. Hugging Face (transcripción mejorada, traducción)
2. OpenAI (DALL-E para imágenes)
3. Spotify API (obtener música)
4. ESPN/NBA Stats API (datos más actualizados)

¿Puedes crear un ExternalAPIManager que:
- Sea compatible con APIManager existente
- Tenga fallbacks configurables
- Cachee resultados
- Maneje rate limits

Ejemplo: generar una imagen única para cada video
```

---

## PROMPT 15: Optimizar Rendimiento

```
El renderizado tarda mucho (5-10 minutos para 45s).

Quiero optimizar:
1. Caché de frames
2. Compresión inteligente
3. Reducir resolución si GPU no disponible
4. Procesar en background
5. Notificaciones de progreso

Benchmarks actuales:
- 45s @ 1080x1920 = 8 min
- 60s @ 1920x1080 = 12 min

Meta: 
- 45s @ 1080x1920 = 3 min
- 60s @ 1920x1080 = 5 min

¿Puedes crear VideoOptimizer?
```

---

## Cómo Usar Estos Prompts

1. **Ve a claude.ai/code**
2. **Escribe `/start`**
3. **Copia uno de los prompts arriba**
4. **Adapta según tu caso**
5. **Claude hace el cambio y explica qué hizo**

---

## Prompts para Debugging

### Si VideoGenerator no carga:
```
Estoy obteniendo este error:
[ERROR MESSAGE]

El archivo está en: [PATH]
Las importaciones son:
[IMPORTS]

¿Qué está mal?
```

### Si Claude genera código inválido:
```
Claude generó esta composición pero da error:
[CODIGO]

Error: [ERROR]

¿Cómo puedo hacerla válida?
```

### Si Remotion falla:
```
Remotion está dando este error:
[STDERR]

Mi composición:
[CODIGO COMPOSICION]

¿Cómo lo arreglo?
```

---

## Tips para Claude Code

1. **Siempre incluye contexto:** Qué archivo, qué función, qué error
2. **Sé específico:** "Mejor manejo de errores" es vago. "Si Remotion timeout, reintentar 3 veces" es claro
3. **Proporciona ejemplos:** Antes/después de código ayuda
4. **Pide explicación:** "¿Cómo funciona esto?" es válido
5. **Iterativo:** Puedes mejorar la solución en múltiples pasos

---

**¡Usa estos prompts para personalizar tu integración según tus necesidades!** 🚀
