"""
================================================================================
CLAUDE PROMPT VALIDATOR - Proyecto Dos Aros
================================================================================
Valida, mejora y optimiza prompts de generación de imagen para el sistema
de avatares (Midjourney / Google ImageFX).
Detecta frases problemáticas y genera reportes de calidad.
================================================================================
"""

import os
import json
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-opus-4-1"

SYSTEM_VALIDADOR = """Eres un experto en prompts de generación de imágenes con IA, especializado en
Midjourney y Google ImageFX para el proyecto Dos Aros.

Tu función es evaluar y mejorar prompts de imagen para avatares deportivos.
Criterios de evaluación:
1. Especificidad visual (iluminación, composición, estilo fotográfico)
2. Coherencia estilística (futurismo deportivo, elegancia analítica)
3. Ausencia de frases que los modelos rechazan (personas reales, marcas, violencia)
4. Optimización técnica para ImageFX (estructura, longitud, vocabulario)
5. Efectividad semántica (qué tan bien describe la imagen deseada)

Responde siempre con JSON válido según el formato solicitado."""


# Frases que ImageFX/Midjourney suelen rechazar o degradan la calidad
FRASES_PROBLEMATICAS_CONOCIDAS = [
    "real person", "celebrity", "NBA player", "famous",
    "brand logo", "nike", "adidas", "realistic face",
    "blood", "violence", "weapon", "NSFW",
    "children", "minor", "underage",
]


class ClaudePromptValidator:
    """Valida y optimiza prompts de generación de imagen para avatares."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.client = anthropic.Anthropic(api_key=api_key)

    def validate_prompt(self, prompt: str) -> dict:
        """
        Valida un prompt y devuelve un score con desglose por criterio.

        Args:
            prompt: Prompt de imagen a validar

        Returns:
            Dict con estructura:
            {
                "score_total": int (1-10),
                "scores": {
                    "especificidad": int,
                    "coherencia": int,
                    "seguridad": int,
                    "tecnico": int,
                    "semantica": int
                },
                "problemas": list[str],
                "fortalezas": list[str],
                "recomendacion": str
            }
        """
        mensaje = (
            f"Valida este prompt de generación de imagen:\n\n"
            f"```\n{prompt}\n```\n\n"
            f"Devuelve SOLO un JSON válido con esta estructura exacta:\n"
            f'{{"score_total": <1-10>, '
            f'"scores": {{"especificidad": <1-10>, "coherencia": <1-10>, '
            f'"seguridad": <1-10>, "tecnico": <1-10>, "semantica": <1-10>}}, '
            f'"problemas": ["..."], "fortalezas": ["..."], "recomendacion": "..."}}'
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=512,
                system=SYSTEM_VALIDADOR,
                messages=[{"role": "user", "content": mensaje}],
            )
            texto = response.content[0].text.strip()
            # Extrae JSON aunque venga envuelto en markdown
            match = re.search(r"\{.*\}", texto, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"score_total": 0, "error": "Respuesta no parseable", "raw": texto}
        except (anthropic.APIError, json.JSONDecodeError) as e:
            print(f"[ClaudePromptValidator] Error validate_prompt: {e}")
            return {"score_total": 0, "error": str(e)}

    def improve_prompt(self, prompt: str, target_score: int = 8) -> str:
        """
        Mejora un prompt hasta alcanzar el score objetivo.

        Args:
            prompt: Prompt original a mejorar
            target_score: Score mínimo objetivo (1-10, default 8)

        Returns:
            Prompt mejorado listo para usar en ImageFX/Midjourney
        """
        mensaje = (
            f"Mejora este prompt de imagen para alcanzar un score de {target_score}/10:\n\n"
            f"```\n{prompt}\n```\n\n"
            f"Mejoras a aplicar:\n"
            f"- Añade detalles de iluminación específicos\n"
            f"- Incluye estilo fotográfico/artístico\n"
            f"- Especifica composición y plano\n"
            f"- Elimina frases ambiguas o problemáticas\n"
            f"- Mantén el concepto central del avatar analista deportivo\n\n"
            f"Devuelve SOLO el prompt mejorado, sin explicaciones."
        )

        try:
            with self.client.messages.stream(
                model=MODELO,
                max_tokens=512,
                thinking={"type": "adaptive"},
                system=SYSTEM_VALIDADOR,
                messages=[{"role": "user", "content": mensaje}],
            ) as stream:
                final = stream.get_final_message()
                for bloque in reversed(final.content):
                    if bloque.type == "text":
                        return bloque.text.strip()
            return prompt
        except anthropic.APIError as e:
            print(f"[ClaudePromptValidator] Error improve_prompt: {e}")
            return prompt

    def optimize_for_imagefx(self, prompt: str) -> str:
        """
        Optimiza un prompt específicamente para Google ImageFX.

        Args:
            prompt: Prompt a optimizar

        Returns:
            Prompt reformateado según las mejores prácticas de ImageFX
        """
        mensaje = (
            f"Optimiza este prompt para Google ImageFX:\n\n"
            f"```\n{prompt}\n```\n\n"
            f"Directrices de ImageFX:\n"
            f"- Estructura: [sujeto], [acción/estado], [escenario], [estilo], [calidad]\n"
            f"- Evita negaciones (no uses 'sin', 'without', 'no')\n"
            f"- Usa adjetivos descriptivos en lugar de comparaciones\n"
            f"- Especifica: 'photorealistic', 'cinematic lighting', 'high detail'\n"
            f"- Longitud óptima: 50-120 palabras\n"
            f"- Idioma: inglés\n\n"
            f"Devuelve SOLO el prompt optimizado en inglés, sin explicaciones."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=384,
                system=SYSTEM_VALIDADOR,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudePromptValidator] Error optimize_for_imagefx: {e}")
            return prompt

    def detect_problematic_phrases(self, prompt: str) -> list[str]:
        """
        Detecta frases que pueden causar rechazo o degradar la calidad en modelos de imagen.

        Args:
            prompt: Prompt a analizar

        Returns:
            Lista de frases problemáticas detectadas (vacía si el prompt es seguro)
        """
        # Detección rápida local primero
        prompt_lower = prompt.lower()
        detectadas_local = [
            frase for frase in FRASES_PROBLEMATICAS_CONOCIDAS
            if frase.lower() in prompt_lower
        ]

        # Detección semántica con Claude para matices
        mensaje = (
            f"Analiza este prompt de imagen y detecta frases que ImageFX o Midjourney "
            f"podrían rechazar o que degraden la calidad:\n\n"
            f"```\n{prompt}\n```\n\n"
            f"Devuelve SOLO una lista JSON de frases problemáticas. "
            f"Si no hay problemas, devuelve []. Ejemplo: [\"real person\", \"brand name\"]"
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=256,
                system=SYSTEM_VALIDADOR,
                messages=[{"role": "user", "content": mensaje}],
            )
            texto = response.content[0].text.strip()
            match = re.search(r"\[.*?\]", texto, re.DOTALL)
            if match:
                detectadas_ia = json.loads(match.group())
                # Combina y deduplica
                todas = list(set(detectadas_local + detectadas_ia))
                return todas
            return detectadas_local
        except (anthropic.APIError, json.JSONDecodeError) as e:
            print(f"[ClaudePromptValidator] Error detect_problematic_phrases: {e}")
            return detectadas_local

    def quality_report(self, prompt: str) -> dict:
        """
        Genera un reporte completo de calidad del prompt con validación, problemas y prompt mejorado.

        Args:
            prompt: Prompt a analizar completamente

        Returns:
            Dict con:
            {
                "prompt_original": str,
                "validacion": dict (resultado de validate_prompt),
                "frases_problematicas": list[str],
                "prompt_optimizado": str,
                "listo_para_usar": bool
            }
        """
        validacion = self.validate_prompt(prompt)
        frases = self.detect_problematic_phrases(prompt)
        score = validacion.get("score_total", 0)

        if score >= 8 and not frases:
            prompt_optimizado = self.optimize_for_imagefx(prompt)
            listo = True
        else:
            prompt_mejorado = self.improve_prompt(prompt, target_score=8)
            prompt_optimizado = self.optimize_for_imagefx(prompt_mejorado)
            listo = score >= 6 and not frases

        return {
            "prompt_original": prompt,
            "validacion": validacion,
            "frases_problematicas": frases,
            "prompt_optimizado": prompt_optimizado,
            "listo_para_usar": listo,
        }


# ── Funciones de integración para bot_consultas.py ──────────────────────────

def validar_prompt_bot(prompt: str) -> dict:
    """
    Wrapper para bot_consultas.py.
    Valida un prompt antes de enviarlo a ImageFX.

    Ejemplo de uso en bot_consultas:
        from src.integrations.claude_prompt_validator import validar_prompt_bot
        resultado = validar_prompt_bot(prompt_generado)
        if resultado["score_total"] >= 7:
            enviar_a_imagefx(prompt)
    """
    validador = ClaudePromptValidator()
    return validador.validate_prompt(prompt)


def optimizar_prompt_bot(prompt: str) -> str:
    """
    Wrapper para bot_consultas.py.
    Optimiza un prompt para ImageFX antes de generar la imagen del avatar.
    """
    validador = ClaudePromptValidator()
    return validador.optimize_for_imagefx(prompt)


def reporte_completo_prompt_bot(prompt: str) -> dict:
    """
    Wrapper para bot_consultas.py.
    Genera reporte completo de calidad y devuelve el prompt listo para producción.
    """
    validador = ClaudePromptValidator()
    return validador.quality_report(prompt)
