# 🚀 INSTALACIÓN RÁPIDA - Editor Pro Max + Dos Aros

**Tiempo estimado: 15 minutos**

---

## ✅ PASO 1: Clonar Editor Pro Max

```bash
cd ~/dos-aros

# Opción A: Clonar repo
git clone https://github.com/Hainrixz/editor-pro-max.git

# Opción B: Añadir como submódulo Git (recomendado)
git submodule add https://github.com/Hainrixz/editor-pro-max.git editor_pro_max
```

---

## ✅ PASO 2: Instalar Dependencias

```bash
# 1. Editor Pro Max dependencies
cd editor_pro_max
npm install
pip install -r requirements.txt
cd ..

# 2. Instalar FFmpeg (si no lo tienes)
sudo apt-get update
sudo apt-get install ffmpeg

# 3. Verificar instalación
ffmpeg -version
npm --version
npx remotion --version
```

---

## ✅ PASO 3: Copiar Archivos de Integración

Crea la estructura de carpetas:

```bash
mkdir -p src/integrations/video_generator
mkdir -p src/prompts/video_prompts
mkdir -p assets/video_output
```

Copia estos archivos (desde los que te proporcioné):

```bash
# Copiar los 3 archivos principales:
cp video_generator.py src/integrations/video_generator/
cp telegram_video_handler.py src/integrations/
```

Crea archivos `__init__.py`:

```bash
# En src/integrations/video_generator/
touch src/integrations/video_generator/__init__.py

# En src/integrations/
touch src/integrations/__init__.py
```

Contenido de `src/integrations/__init__.py`:

```python
from .video_generator.video_generator import VideoGenerator
from .telegram_video_handler import TelegramVideoHandler, setup_video_handlers

__all__ = ['VideoGenerator', 'TelegramVideoHandler', 'setup_video_handlers']
```

Contenido de `src/integrations/video_generator/__init__.py`:

```python
from .video_generator import VideoGenerator

__all__ = ['VideoGenerator']
```

---

## ✅ PASO 4: Actualizar tu Bot de Telegram

En tu archivo principal de bot (ej: `automation/bot_manager.py` o donde hayas definido la aplicación):

```python
# Importar
from src.integrations import setup_video_handlers
from src.integrations import VideoGenerator

# En tu función que configura handlers:
def setup_all_handlers(application):
    """Configura todos los handlers del bot"""
    
    # ... tus handlers existentes ...
    
    # Inicializar VideoGenerator
    video_gen = VideoGenerator()
    
    # Configurar handlers de video
    setup_video_handlers(application, video_gen)
    
    print("✅ Todos los handlers configurados")

# En tu main():
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    app = Application.builder().token(TOKEN).build()
    
    # Configurar todos los handlers
    setup_all_handlers(app)
    
    # Iniciar
    print("🤖 Bot iniciado...")
    app.run_polling()
```

---

## ✅ PASO 5: Verificar Instalación

```bash
# Test 1: Verificar importes
python -c "
from src.integrations import VideoGenerator
print('✅ VideoGenerator importado')
"

# Test 2: Verificar APIManager
python -c "
from src.utils.api_manager import APIManager
api = APIManager()
api.print_status()
"

# Test 3: Verificar BD local
python -c "
from src.database.database import consultar_db_local
resultado = consultar_db_local('SELECT COUNT(*) FROM nba_stats')
print(f'✅ BD: {resultado}')
"

# Test 4: Generar video de prueba
python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
video = gen.generar_video('Crea un video de prueba', usuario_id='test_001')
print(f'Video: {video}')
"
```

Si todo está ✅, estás listo.

---

## 🎯 Uso en Telegram

```
Usuario escribe:
/video Top 3 tiradores 3P NBA esta semana

El bot:
1. Captura la instrucción
2. Consulta tu SQLite
3. Claude genera composición
4. Remotion renderiza
5. Envía video al usuario
```

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| "ModuleNotFoundError: No module named 'src'" | Ejecuta desde raíz de proyecto: `cd ~/dos-aros` |
| "ffmpeg not found" | `sudo apt-get install ffmpeg` |
| "npm: command not found" | Instala Node.js: `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash -` && `sudo apt-get install nodejs` |
| "Remotion command not found" | En `editor_pro_max/`: `npm install` |
| "API error: GEMINI_API_KEY" | Verifica `.env` tiene `GEMINI_API_KEY=...` |
| "BD connection error" | Verifica que `DB_PATH` en `.env` apunta al SQLite correcto |

---

## 📊 Verificar que funciona todo

```bash
# 1. Ver estado completo
python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
print('✅ Sistema listo')
"

# 2. Ejecutar tu bot
python src/app/main.py &

# 3. Enviar mensaje en Telegram
/video Prueba de generación

# 4. Ver logs
tail -f logs/bot.log  # Si tienes logs configurados
```

---

## 🚀 Próximas Mejoras (Opcional)

### Cola de renderizado
```python
# Para evitar bloqueos cuando hay muchos videos
from queue import Queue
from threading import Thread

class VideoGeneratorWithQueue(VideoGenerator):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.renderer = Thread(self._render_worker, daemon=True)
        self.renderer.start()
```

### Notificaciones de progreso
```python
# Actualizar mensaje de Telegram en tiempo real
async def actualizar_progreso(self, mensaje, progreso):
    # Editar el mensaje anterior
    await mensaje.edit_text(f"⏳ {progreso}%...")
```

### Compresión automática
```bash
# Después de renderizar:
ffmpeg -i video.mp4 -vcodec libx264 -crf 28 video_compressed.mp4
```

---

## 📞 Soporte

Si algo falla:

1. **Verifica logs:**
   ```bash
   grep -r "ERROR\|error\|Exception" logs/
   ```

2. **Test individual:**
   ```python
   from src.integrations import VideoGenerator
   gen = VideoGenerator()
   gen.generar_video("Tu instrucción", usuario_id="test")
   ```

3. **Check APIs:**
   ```python
   from src.utils.api_manager import APIManager
   api = APIManager()
   api.print_status()
   ```

4. **Check BD:**
   ```bash
   sqlite3 /path/to/dosaros_local.db "SELECT COUNT(*) FROM nba_stats;"
   ```

---

**¡Listo! Tu sistema está integrado. Prueba enviando un mensaje a tu bot en Telegram.** 🚀
