"""
================================================================================
PROMPT HILO X - Proyecto Dos Aros
================================================================================
Genera el prompt para el hilo diario de X (Twitter).
Futura evolución: cargar estructura desde DB (tabla: prompts, id: hilo_x_v1)
================================================================================
"""

from src.prompts.system_persona import get_persona_completa

def get_prompt_hilo(fecha_display, nba_data, euro_data, proximos_euro_data, perlas_data, top_data, historico_data):
    """
    Genera el prompt completo para el hilo de X.

    Args:
        fecha_display: fecha en formato DD/MM/YYYY
        nba_data: lista de resultados NBA
        euro_data: lista de resultados Euroliga
        perlas_data: lista de cazadores de triples
        top_data: lista de mejores actuaciones
        historico_data: dato histórico de la DB

    Returns:
        str: prompt listo para enviar a la IA
    """
    persona = get_persona_completa()

    return f"""
{persona}

═══════════════════════════════════════
TAREA: HILO X DEL {fecha_display}
═══════════════════════════════════════

DATOS DISPONIBLES:
- Resultados NBA: {nba_data}
- Resultados Euroliga: {euro_data}
- Cazadores de triples NBA: {perlas_data}
- Mejores actuaciones NBA: {top_data}
- Dato histórico de la DB: {historico_data}

ESTRUCTURA DEL HILO (5-6 tweets):

TWEET 1 — GANCHO OBLIGATORIO
No empieces con "Anoche en la NBA...".
Empieza con algo que dé ganas de leer el siguiente.
Un dato que sorprende, una contradicción, una frase que provoca.

TWEET 2 — NBA con personalidad
Los resultados más relevantes. Contados, no listados.
Máximo 2-3 partidos. El dato que importa, no el acta notarial.

TWEET 3 — Euroliga

Si la próxima jornada es en más de 2 días desde {fecha_display}: omite este tweet.
NO repitas "no hubo partidos" si ya está implícito.
Si hubo partidos ayer: el más relevante con el dato clave.
Si no hubo partidos pero se juega pronto, usa EXACTAMENTE estas fechas y equipos (no inventes):
Próximos partidos: {proximos_euro_data}
menciona 2-3 partidos atractivos con fecha. Ejemplo: 
"El 24/03 vuelve la Euroliga. BAR-IST y PAM-OLY. Apunta."


TWEET 4 — La perla del día
La actuación más llamativa con el dato exacto.
Sin adornar lo que ya es suficientemente bueno.

TWEET 5 — Dato histórico o comparativa
Algo que ponga en contexto lo de ayer. Un récord, una rareza, una tendencia.

TWEET 6 — Cierre (fuerte o anticlimático, nunca neutro)
Una pregunta que genere debate con un ángulo concreto.
Nunca: "¿Qué opináis?" a secas.

REGLAS DE FORMATO:
- Máximo 250 caracteres por tweet
- Empieza cada tweet con su número: 1/, 2/, 3/...
- Sin hashtags
- Máximo 1 emoji por tweet, solo si aporta
- Separa cada tweet con una línea en blanco
- SOLO los tweets. Sin explicaciones ni comentarios extra.
- OBLIGATORIO: cuenta los caracteres. Ningún tweet puede superar 250 caracteres.
  Si es largo, córtalo. El ritmo importa más que la información completa.

CRÍTICO — LÍMITE DE CARACTERES:
    Antes de escribir cada tweet, cuenta los caracteres.
    Máximo 280 caracteres por tweet (límite real de X).
    Si supera 280, recorta. El ritmo importa más que la información completa.
    Una frase buena y corta vale más que dos frases mediocres.
"""
