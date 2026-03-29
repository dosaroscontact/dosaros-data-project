import sqlite3
import random
from datetime import datetime

def get_avatar_prompt(team_name=None):
    """Obtiene prompt de avatar por equipo o aleatorio"""
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    cursor = conn.cursor()
    
    if team_name:
        # Prompt específico
        result = cursor.execute('''
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            WHERE LOWER(team_name) LIKE LOWER(?)
            LIMIT 1
        ''', (f'%{team_name}%',)).fetchone()
    else:
        # Aleatorio
        result = cursor.execute('''
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            ORDER BY RANDOM()
            LIMIT 1
        ''').fetchone()
    
    conn.close()
    return result

def get_today_avatars(limit=5):
    """Obtiene N prompts aleatorios"""
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    cursor = conn.cursor()
    
    results = cursor.execute('''
        SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
        FROM avatar_prompts
        ORDER BY RANDOM()
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    return results

def format_prompt_message(team_name, scene_type, prompt_text, avatar_url, logo_url):
    """Formatea mensaje para Telegram"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    message = f"""
🎨 **DOS AROS - AVATAR GENERATOR**

📍 **Equipo:** {team_name}
📊 **Tipo:** {scene_type}
⏱️ **Generado:** {timestamp}

🖼️ **AVATAR REFERENCE:**
{avatar_url}

📌 **LOGO:**
{logo_url}

📝 **PROMPT PARA GOOGLE IMAGEFX:**
```
{prompt_text}
```

✅ **INSTRUCCIONES:**
1. Copia el prompt completo
2. Abre Google ImageFX (imagegeneration.dev)
3. Pega el prompt + adjunta avatar URL como imagen de referencia
4. Genera imagen
5. Descarga y publica en redes
"""
    return message

# Ejemplo de uso en Telegram bot (con python-telegram-bot)
"""
Integración con tu bot:

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def avatar_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        team = ' '.join(context.args)
        result = get_avatar_prompt(team)
    else:
        result = get_avatar_prompt()
    
    if result:
        team_name, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_prompt_message(team_name, scene_type, prompt_text, avatar_url, logo_url)
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Equipo no encontrado")

async def avatar_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_avatar_prompt()
    if result:
        team_name, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_prompt_message(team_name, scene_type, prompt_text, avatar_url, logo_url)
        await update.message.reply_text(message, parse_mode='Markdown')

async def avatar_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = get_today_avatars(5)
    if results:
        for result in results:
            team_name, scene_type, prompt_text, avatar_url, logo_url = result
            message = format_prompt_message(team_name, scene_type, prompt_text, avatar_url, logo_url)
            await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ No hay prompts disponibles")

# En main():
app.add_handler(CommandHandler('avatar_prompt', avatar_prompt))
app.add_handler(CommandHandler('avatar_random', avatar_random))
app.add_handler(CommandHandler('avatar_today', avatar_today))
"""

if __name__ == "__main__":
    # Test
    print("🧪 TEST: Avatar Random")
    result = get_avatar_prompt()
    if result:
        team_name, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_prompt_message(team_name, scene_type, prompt_text, avatar_url, logo_url)
        print(message)