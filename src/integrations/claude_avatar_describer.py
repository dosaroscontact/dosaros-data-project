"""
================================================================================
CLAUDE AVATAR DESCRIBER - Proyecto Dos Aros
================================================================================
Genera descripciones, backstories y variaciones de escena para el sistema
de avatares de equipos NBA/EuroLeague.
Integra con avatar_prompt_generator.py y bot_consultas.py.
================================================================================
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-opus-4-1"

SYSTEM_AVATAR = """Eres el director creativo del sistema de avatares de Dos Aros.
El avatar es un personaje analista de baloncesto: elegante, sofisticado, datos en mano.
Filosofía visual: futurismo deportivo + identidad de equipo + narrativa estadística.
Tus descripciones deben:
- Ser cinematográficas y específicas (iluminación, composición, texturas)
- Incorporar los colores del equipo de forma natural en la escena
- Mantener coherencia con el universo visual de Dos Aros
- Evitar referencias de personas reales o marcas registradas
- Responder en español, con términos técnicos de fotografía/arte en inglés"""


class ClaudeAvatarDescriber:
    """Genera descripciones y variaciones de escena para avatares de equipos."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.client = anthropic.Anthropic(api_key=api_key)

    def describe_avatar(
        self,
        team_name: str,
        scene_type: str,
        colors: dict,
    ) -> str:
        """
        Genera una descripción cinematográfica del avatar para un equipo.

        Args:
            team_name: Nombre del equipo (ej. "Los Angeles Lakers")
            scene_type: Tipo de escena (ej. "análisis pre-partido", "celebración", "sala de datos")
            colors: Dict con colores del equipo (ej. {"primary": "#552583", "secondary": "#FDB927"})

        Returns:
            Descripción detallada para generar imagen con Midjourney/ImageFX
        """
        colores_str = ", ".join(f"{k}: {v}" for k, v in colors.items())
        mensaje = (
            f"Describe el avatar del analista de Dos Aros para el equipo {team_name}.\n"
            f"Escena: {scene_type}\n"
            f"Colores del equipo: {colores_str}\n\n"
            f"Genera una descripción visual detallada (200-300 palabras) que sirva como prompt "
            f"para generación de imagen. Incluye: postura, vestimenta, escenario, iluminación, "
            f"atmósfera y cómo los colores del equipo aparecen en la escena."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=512,
                system=SYSTEM_AVATAR,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeAvatarDescriber] Error API describe_avatar: {e}")
            return ""

    def generate_scene_variation(self, team_name: str, base_scene: str) -> str:
        """
        Genera una variación creativa de una escena base existente.

        Args:
            team_name: Nombre del equipo
            base_scene: Descripción de la escena base a variar

        Returns:
            Nueva variación de la escena con elementos distintos
        """
        mensaje = (
            f"Equipo: {team_name}\n"
            f"Escena base:\n{base_scene}\n\n"
            f"Genera una VARIACIÓN de esta escena. Mantén la esencia del equipo pero cambia: "
            f"ángulo de cámara, hora del día, elementos decorativos o actividad del personaje. "
            f"La variación debe sentirse fresca pero coherente con la identidad del equipo."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=512,
                system=SYSTEM_AVATAR,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeAvatarDescriber] Error API generate_scene_variation: {e}")
            return ""

    def create_backstory(self, team_name: str, scene_type: str) -> str:
        """
        Crea la historia de fondo narrativa del avatar para un equipo/escena.

        Args:
            team_name: Nombre del equipo
            scene_type: Tipo de escena o contexto narrativo

        Returns:
            Backstory del personaje (quién es, qué hace, por qué está en esa escena)
        """
        mensaje = (
            f"Crea el backstory narrativo del analista-avatar de Dos Aros que representa a {team_name}.\n"
            f"Contexto de escena: {scene_type}\n\n"
            f"El backstory debe explicar: quién es este analista, qué datos está procesando, "
            f"qué momento del partido/temporada captura la escena, y por qué esta imagen "
            f"representa la esencia analítica del equipo {team_name}. "
            f"Máximo 150 palabras. Tono: periodismo deportivo de alto nivel."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=384,
                system=SYSTEM_AVATAR,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeAvatarDescriber] Error API create_backstory: {e}")
            return ""

    def suggest_pose(self, team_name: str, scene_type: str) -> str:
        """
        Sugiere la postura/composición ideal para el avatar según equipo y escena.

        Args:
            team_name: Nombre del equipo
            scene_type: Tipo de escena

        Returns:
            Descripción concreta de la postura, gesto y composición recomendada
        """
        mensaje = (
            f"Sugiere la postura y composición visual óptima para el avatar de {team_name} "
            f"en una escena de tipo '{scene_type}'.\n\n"
            f"Especifica: posición del cuerpo, dirección de la mirada, gesto de las manos, "
            f"elementos que sostiene o señala, y cómo encuadrar la figura en el frame. "
            f"Responde en 80-120 palabras, como una indicación de director de fotografía."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=256,
                system=SYSTEM_AVATAR,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeAvatarDescriber] Error API suggest_pose: {e}")
            return ""


# ── Funciones de integración para bot_consultas.py ──────────────────────────

def generar_descripcion_avatar_bot(
    team_name: str,
    scene_type: str,
    colors: dict,
) -> str:
    """
    Wrapper para bot_consultas.py.
    Genera descripción de avatar al responder consultas sobre equipos.

    Ejemplo de uso en bot_consultas:
        from src.integrations.claude_avatar_describer import generar_descripcion_avatar_bot
        desc = generar_descripcion_avatar_bot("Lakers", "análisis", {"primary": "#552583"})
    """
    describer = ClaudeAvatarDescriber()
    return describer.describe_avatar(team_name, scene_type, colors)


def backstory_equipo_bot(team_name: str, scene_type: str = "análisis de temporada") -> str:
    """
    Wrapper para bot_consultas.py.
    Genera el backstory narrativo del avatar cuando se consulta sobre un equipo.
    """
    describer = ClaudeAvatarDescriber()
    return describer.create_backstory(team_name, scene_type)
