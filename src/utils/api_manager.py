"""
================================================================================
API MANAGER - Gestor Centralizado de APIs para Proyecto Dos Aros
================================================================================
Propósito: Interface única y segura para acceder a todas las APIs configuradas
en .env. Maneja errores, fallbacks y logging centralizado.

Uso:
    from src.utils.api_manager import APIManager
    
    api = APIManager()
    
    # Usar Gemini
    response = api.gemini(prompt="Analiza estos datos...")
    
    # Usar múltiples APIs con fallback automático
    response = api.generate_text(prompt="...", providers=["gemini", "claude", "groq"])
    
    # Generar imagen
    image_url = api.generate_image(prompt="...", provider="together")
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Importar clientes de APIs
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None

try:
    import groq
except ImportError:
    groq = None


# ============================================================================
# CONFIGURACIÓN Y LOGGING
# ============================================================================

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ============================================================================
# CLASE PRINCIPAL: API MANAGER
# ============================================================================

class APIManager:
    """
    Gestor centralizado para todas las APIs del proyecto Dos Aros.
    
    Características:
    - Configuración segura desde .env
    - Fallback automático entre proveedores
    - Manejo de rate limiting y errores
    - Logging centralizado
    - Cache de clientes (evita reinicializaciones)
    
    Proveedores soportados:
    
    LLMs:
        - gemini (Google)
        - claude (Anthropic)
        - openai (ChatGPT)
        - groq (Llama/Mixtral)
        - deepseek
        - kimi
        - grok
    
    Imágenes:
        - together (Flux.1 Schnell)
        - pollinations (Free)
    
    Audio:
        - elevenlabs
        - playht
    
    Vídeo:
        - luma
        - heygen
    """
    
    def __init__(self):
        """Inicializa el API Manager y valida configuración."""
        self.config = self._load_config()
        self.clients = {}  # Cache de clientes instanciados
        self._init_clients()
        logger.info("✅ API Manager inicializado correctamente")
    
    
    def _load_config(self) -> Dict[str, str]:
        """Carga todas las configuraciones desde .env."""
        config = {
            # LLMs
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
            
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            
            'claude_api_key': os.getenv('CLAUDE_API_KEY'),
            'claude_model': os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-latest'),
            
            'groq_api_key': os.getenv('GROQ_API_KEY'),
            'groq_model': os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile'),
            
            'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
            'deepseek_model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            
            'kimi_api_key': os.getenv('KIMI_API_KEY'),
            'kimi_model': os.getenv('KIMI_MODEL', 'moonshot-v1-128k'),
            
            'grok_api_key': os.getenv('GROK_API_KEY'),
            'grok_model': os.getenv('GROK_MODEL', 'grok-beta'),
            
            # Imágenes
            'together_api_key': os.getenv('TOGETHER_API_KEY'),
            'together_model': os.getenv('TOGETHER_MODEL', 'black-forest-labs/FLUX.1-schnell'),
            'pollinations_enabled': os.getenv('POLLINATIONS_ENABLED', 'true').lower() == 'true',
            
            # Audio
            'elevenlabs_api_key': os.getenv('ELEVENLABS_API_KEY'),
            'elevenlabs_voice_id': os.getenv('ELEVENLABS_VOICE_ID', 'default'),
            'playht_api_key': os.getenv('PLAYHT_API_KEY'),
            
            # Vídeo
            'luma_api_key': os.getenv('LUMA_API_KEY'),
            'heygen_api_key': os.getenv('HEYGEN_API_KEY'),
            
            # Datos deportivos
            'nba_enabled': os.getenv('NBA_API_ENABLED', 'true').lower() == 'true',
            'euro_enabled': os.getenv('EURO_API_ENABLED', 'true').lower() == 'true',
            
            # Local
            'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'ollama_enabled': os.getenv('OLLAMA_ENABLED', 'false').lower() == 'true',
        }
        return config
    
    
    def _init_clients(self):
        """Inicializa clientes de APIs configuradas."""
        # Google Gemini
        if self.config.get('gemini_api_key'):
            try:
                genai.configure(api_key=self.config['gemini_api_key'])
                self.clients['gemini'] = genai.GenerativeModel(self.config['gemini_model'])
                logger.info("✅ Gemini cliente inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando Gemini: {e}")
        
        # Anthropic Claude
        if self.config.get('claude_api_key'):
            try:
                if anthropic:
                    self.clients['claude'] = anthropic.Anthropic(
                        api_key=self.config['claude_api_key']
                    )
                    logger.info("✅ Claude cliente inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando Claude: {e}")
        
        # OpenAI
        if self.config.get('openai_api_key'):
            try:
                if openai:
                    openai.api_key = self.config['openai_api_key']
                    self.clients['openai'] = openai.Client(
                        api_key=self.config['openai_api_key']
                    )
                    logger.info("✅ OpenAI cliente inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando OpenAI: {e}")
        
        # Groq
        if self.config.get('groq_api_key'):
            try:
                if groq:
                    self.clients['groq'] = groq.Groq(
                        api_key=self.config['groq_api_key']
                    )
                    logger.info("✅ Groq cliente inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando Groq: {e}")
    
    
    # ========================================================================
    # MÉTODOS: LLMs - ANÁLISIS Y GENERACIÓN DE TEXTO
    # ========================================================================
    
    def gemini(self, prompt: str, system_prompt: str = None) -> str:
        """
        Usa Google Gemini para generar respuesta.
        
        Args:
            prompt: Pregunta o instrucción
            system_prompt: Contexto adicional (opcional)
            
        Returns:
            Respuesta de Gemini como string
            
        Raises:
            ValueError: Si Gemini no está configurado
        """
        if 'gemini' not in self.clients:
            raise ValueError("Gemini no está configurado. Verifica GEMINI_API_KEY en .env")
        
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.clients['gemini'].generate_content(full_prompt)
            logger.debug(f"✅ Gemini: {len(response.text)} caracteres generados")
            return response.text
        except Exception as e:
            logger.error(f"❌ Error en Gemini: {e}")
            raise
    
    
    def claude(self, prompt: str, system_prompt: str = None, max_tokens: int = 2048) -> str:
        """
        Usa Anthropic Claude para generar respuesta.
        
        Args:
            prompt: Pregunta o instrucción
            system_prompt: Contexto adicional (opcional)
            max_tokens: Número máximo de tokens en respuesta
            
        Returns:
            Respuesta de Claude como string
        """
        if 'claude' not in self.clients:
            raise ValueError("Claude no está configurado. Verifica CLAUDE_API_KEY en .env")
        
        try:
            response = self.clients['claude'].messages.create(
                model=self.config['claude_model'],
                max_tokens=max_tokens,
                system=system_prompt or "Eres un asistente experto en análisis de datos deportivos.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.content[0].text
            logger.debug(f"✅ Claude: {len(result)} caracteres generados")
            return result
        except Exception as e:
            logger.error(f"❌ Error en Claude: {e}")
            raise
    
    
    def openai(self, prompt: str, system_prompt: str = None) -> str:
        """
        Usa OpenAI ChatGPT para generar respuesta.
        
        Args:
            prompt: Pregunta o instrucción
            system_prompt: Contexto adicional (opcional)
            
        Returns:
            Respuesta de GPT como string
        """
        if 'openai' not in self.clients:
            raise ValueError("OpenAI no está configurado. Verifica OPENAI_API_KEY en .env")
        
        try:
            response = self.clients['openai'].chat.completions.create(
                model=self.config['openai_model'],
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt or "Eres un asistente experto."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content
            logger.debug(f"✅ OpenAI: {len(result)} caracteres generados")
            return result
        except Exception as e:
            logger.error(f"❌ Error en OpenAI: {e}")
            raise
    
    
    def groq(self, prompt: str, system_prompt: str = None) -> str:
        """
        Usa Groq (Llama/Mixtral) para generar respuesta RÁPIDAMENTE.
        
        Args:
            prompt: Pregunta o instrucción
            system_prompt: Contexto adicional (opcional)
            
        Returns:
            Respuesta de Groq como string
            
        Note: Especializado en velocidad (<1s), ideal para Telegram real-time.
        """
        if 'groq' not in self.clients:
            raise ValueError("Groq no está configurado. Verifica GROQ_API_KEY en .env")
        
        try:
            response = self.clients['groq'].chat.completions.create(
                model=self.config['groq_model'],
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt or "Eres un asistente rápido y preciso."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024
            )
            result = response.choices[0].message.content
            logger.debug(f"✅ Groq: {len(result)} caracteres generados (velocidad: <1s)")
            return result
        except Exception as e:
            logger.error(f"❌ Error en Groq: {e}")
            raise
    
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        providers: List[str] = None
    ) -> str:
        """
        Genera texto usando múltiples proveedores con fallback automático.
        
        Args:
            prompt: Pregunta o instrucción
            system_prompt: Contexto adicional
            providers: Lista de proveedores en orden de preferencia.
                      Default: ['gemini', 'claude', 'groq', 'openai']
                      
        Returns:
            Respuesta del primer proveedor disponible
            
        Example:
            # Intenta Gemini, si falla Claude, luego Groq
            response = api.generate_text(
                prompt="...",
                providers=['gemini', 'claude', 'groq']
            )
        """
        providers = providers or ['gemini', 'claude', 'groq', 'openai']
        
        for provider in providers:
            try:
                if provider == 'gemini':
                    return self.gemini(prompt, system_prompt)
                elif provider == 'claude':
                    return self.claude(prompt, system_prompt)
                elif provider == 'openai':
                    return self.openai(prompt, system_prompt)
                elif provider == 'groq':
                    return self.groq(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"⚠️ {provider} falló: {e}, intentando siguiente...")
        
        raise ValueError(f"Ningún proveedor disponible de {providers}")
    
    
    # ========================================================================
    # MÉTODOS: IMÁGENES
    # ========================================================================
    
    def generate_image(
        self,
        prompt: str,
        provider: str = "together",
        size: str = "1024x1024"
    ) -> str:
        """
        Genera imagen usando el proveedor especificado.
        
        Args:
            prompt: Descripción de la imagen
            provider: 'together' (Flux.1 Schnell) o 'pollinations' (free)
            size: Tamaño de imagen (ej: "1024x1024")
            
        Returns:
            URL de la imagen generada
            
        Note: Together es más rápido y con mejor calidad. 
              Pollinations es gratis pero sin KEY requerida.
        """
        if provider == "pollinations":
            # Pollinations es free y no requiere KEY
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            logger.info(f"✅ Imagen Pollinations generada: {url}")
            return url
        
        elif provider == "together":
            if not self.config.get('together_api_key'):
                raise ValueError("TOGETHER_API_KEY no configurada")
            
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.config['together_api_key']}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": self.config['together_model'],
                    "prompt": prompt,
                    "steps": 1,  # Schnell usa 1 paso
                    "width": int(size.split('x')[0]),
                    "height": int(size.split('x')[1])
                }
                response = requests.post(
                    "https://api.together.xyz/inference",
                    headers=headers,
                    json=data
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ Imagen Together generada")
                    return result.get('output', {}).get('images', [None])[0]
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"❌ Error en Together: {e}")
                raise
        
        else:
            raise ValueError(f"Proveedor desconocido: {provider}")
    
    
    # ========================================================================
    # MÉTODOS: AUDIO (TEXT-TO-SPEECH)
    # ========================================================================
    
    def text_to_speech(
        self,
        text: str,
        provider: str = "elevenlabs",
        voice_id: Optional[str] = None
    ) -> bytes:
        """
        Convierte texto a audio usando el proveedor especificado.
        
        Args:
            text: Texto a convertir
            provider: 'elevenlabs' o 'playht'
            voice_id: ID de voz (opcional, usa default si no se especifica)
            
        Returns:
            Audio en bytes (idealmente MP3 o WAV)
            
        Note: ElevenLabs tiene mejor calidad. Play.ht es mejor para clonación.
        """
        if provider == "elevenlabs":
            if not self.config.get('elevenlabs_api_key'):
                raise ValueError("ELEVENLABS_API_KEY no configurada")
            
            try:
                import requests
                voice_id = voice_id or self.config.get('elevenlabs_voice_id', 'default')
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                headers = {
                    "xi-api-key": self.config['elevenlabs_api_key'],
                    "Content-Type": "application/json"
                }
                data = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    logger.info("✅ Audio ElevenLabs generado")
                    return response.content
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Error en ElevenLabs: {e}")
                raise
        
        else:
            raise ValueError(f"Proveedor TTS desconocido: {provider}")
    
    
    # ========================================================================
    # MÉTODOS: UTILIDAD
    # ========================================================================
    
    def get_status(self) -> Dict[str, bool]:
        """
        Retorna estado de configuración de todos los proveedores.
        
        Returns:
            Dict con 'provider': True/False para cada uno configurado
            
        Example:
            status = api.get_status()
            print(status)
            # {'gemini': True, 'claude': False, 'openai': True, ...}
        """
        return {
            'gemini': bool(self.config.get('gemini_api_key')),
            'claude': bool(self.config.get('claude_api_key')),
            'openai': bool(self.config.get('openai_api_key')),
            'groq': bool(self.config.get('groq_api_key')),
            'deepseek': bool(self.config.get('deepseek_api_key')),
            'kimi': bool(self.config.get('kimi_api_key')),
            'grok': bool(self.config.get('grok_api_key')),
            'together': bool(self.config.get('together_api_key')),
            'pollinations': self.config.get('pollinations_enabled', False),
            'elevenlabs': bool(self.config.get('elevenlabs_api_key')),
            'playht': bool(self.config.get('playht_api_key')),
            'luma': bool(self.config.get('luma_api_key')),
            'heygen': bool(self.config.get('heygen_api_key')),
            'nba_api': self.config.get('nba_enabled', False),
            'euro_api': self.config.get('euro_enabled', False),
            'ollama': self.config.get('ollama_enabled', False),
        }
    
    
    def print_status(self):
        """Imprime estado de configuración de forma legible."""
        status = self.get_status()
        print("\n" + "="*60)
        print("📊 ESTADO DE PROVEEDORES API - PROYECTO DOS AROS")
        print("="*60)
        
        categories = {
            'LLMs': ['gemini', 'claude', 'openai', 'groq', 'deepseek', 'kimi', 'grok'],
            'Imágenes': ['together', 'pollinations'],
            'Audio': ['elevenlabs', 'playht'],
            'Vídeo': ['luma', 'heygen'],
            'Datos': ['nba_api', 'euro_api'],
            'Local': ['ollama'],
        }
        
        for category, providers in categories.items():
            print(f"\n{category}:")
            for provider in providers:
                emoji = "✅" if status.get(provider) else "❌"
                print(f"  {emoji} {provider.upper():15} {'Configurado' if status.get(provider) else 'NO configurado'}")
        
        print("\n" + "="*60 + "\n")


# ============================================================================
# FUNCIÓN DE PRUEBA
# ============================================================================

def test_api_manager():
    """Función de prueba para validar la configuración."""
    try:
        api = APIManager()
        api.print_status()
        
        # Test Gemini si está disponible
        if api.get_status()['gemini']:
            print("\n🧪 Test Gemini...")
            response = api.gemini("Di 'Hola Dos Aros' en una sola frase corta.")
            print(f"✅ Respuesta: {response[:100]}...")
    
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        raise


if __name__ == "__main__":
    # Ejecutar prueba
    test_api_manager()
