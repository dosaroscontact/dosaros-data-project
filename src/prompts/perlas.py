"""
================================================================================
PROMPT PERLAS - Proyecto Dos Aros
================================================================================
Prompt para narrar las perlas del día con el estilo Dos Aros.
Futura evolución: cargar desde DB (tabla: prompts, id: perlas_v1)
================================================================================
"""

from src.prompts.system_persona import get_persona


def get_prompt_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro):
    """
    Genera el prompt para narrar las perlas del día.
    Por ahora las perlas se formatean directamente en insight_generator.py.
    Este prompt se usará cuando queramos que la IA las narre con estilo Dos Aros.
    """
    persona = get_persona()

    return f"""
{persona}

TAREA: Narra las siguientes perlas del {fecha_display} con el estilo Dos Aros.
Breve, directo, con el dato. Máximo 2 líneas por perla.

PERLAS NBA: {perlas_nba}
PERLAS EUROLIGA: {perlas_euro}
PRÓXIMOS EURO: {proximos_euro}

Formato: lista de viñetas, una por perla. Sin numeración. Sin hashtags.
"""
