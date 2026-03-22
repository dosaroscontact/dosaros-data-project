"""
================================================================================
PROMPT STORIES/REELS - Proyecto Dos Aros
================================================================================
Prompt para generar guiones de stories e Instagram Reels.
Futura evolución: cargar desde DB (tabla: prompts, id: stories_v1)
================================================================================
"""

from src.prompts.system_persona import get_persona_completa


def get_prompt_story(fecha_display, datos, enfoque=None):
    """
    Genera el prompt para el guion de una story/reel.

    Args:
        fecha_display: fecha en formato DD/MM/YYYY
        datos: dict con datos del día (nba, euro, perlas)
        enfoque: str opcional — tema concreto sugerido por el usuario

    Returns:
        str: prompt listo para enviar a la IA
    """
    persona = get_persona_completa()

    enfoque_str = f"\nENFOQUE SUGERIDO: {enfoque}" if enfoque else "\nENFOQUE: elige el momento más llamativo del día"

    return f"""
{persona}

TAREA: Guion para story/reel de Instagram del {fecha_display}.
{enfoque_str}

DATOS: {datos}

FORMATO DEL GUION:
- Duración: 30-45 segundos
- Estructura: Hook (3s) → Datos (20s) → Remate (7s)
- Texto en pantalla: frases cortas, máximo 6 palabras por línea
- Voz en off: tono natural, como si lo contaras a un amigo
- Sin hashtags en el guion

OUTPUT:
[TEXTO EN PANTALLA]
línea 1
línea 2
...

[VOZ EN OFF]
Texto del audio narrado...

[CIERRE]
Frase final en pantalla
"""
