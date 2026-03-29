# Lee el bot actual
with open('src/automation/bot_consultas.py', 'r') as f:
    contenido = f.read()

# Verificar si ya tiene funciones de avatar
if 'def get_avatar_prompt' in contenido:
    print("✅ Bot ya tiene comandos de avatar")
    exit(0)

# Buscar dónde insertar (antes de "# ============================================================================")
# Buscar la sección de COMANDOS /video
insertar_antes = "def _procesar_comando_video(instruccion: str):"

# Código a insertar (funciones de avatar)
codigo_avatar = '''
# ============================================================================
# FUNCIONES AVATAR
# ============================================================================

def get_avatar_prompt(team_name=None):
    """Obtiene prompt de avatar por equipo o aleatorio"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if team_name:
        result = cursor.execute(\'\'\'
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            WHERE LOWER(team_name) LIKE LOWER(?)
            LIMIT 1
        \'\'\', (f\'%{team_name}%\',)).fetchone()
    else:
        result = cursor.execute(\'\'\'
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            ORDER BY RANDOM()
            LIMIT 1
        \'\'\').fetchone()
    
    conn.close()
    return result


def get_today_avatars(limit=5):
    """Obtiene N prompts aleatorios"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    results = cursor.execute(\'\'\'
        SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
        FROM avatar_prompts
        ORDER BY RANDOM()
        LIMIT ?
    \'\'\', (limit,)).fetchall()
    
    conn.close()
    return results


def format_avatar_message(team_name, scene_type, prompt_text, avatar_url, logo_url):
    """Formatea mensaje de avatar para Telegram"""
    timestamp = datetime.now().strftime(\'%Y-%m-%d %H:%M\')
    
    message = f"""
<b>🎨 DOS AROS - AVATAR GENERATOR</b>

<b>📍 Equipo:</b> {team_name}
<b>📊 Tipo:</b> {scene_type}
<b>⏱️ Generado:</b> {timestamp}

<b>🖼️ AVATAR REFERENCE:</b>
{avatar_url}

<b>📌 LOGO:</b>
{logo_url}

<b>📝 PROMPT PARA GOOGLE IMAGEFX:</b>

<code>{prompt_text}</code>

<b>✅ INSTRUCCIONES:</b>
1. Copia el prompt completo
2. Abre Google ImageFX (imagegeneration.dev)
3. Pega el prompt + adjunta avatar URL como imagen
4. Genera imagen
5. Descarga y publica en redes
"""
    return message


def _procesar_comando_avatar_prompt(team_name: str):
    """Procesa /avatar_prompt [team]"""
    if not team_name:
        _enviar("❌ Uso: /avatar_prompt [equipo]\\nEj: /avatar_prompt Lakers")
        return
    
    print(f"\\n→ Avatar prompt: {team_name}")
    result = get_avatar_prompt(team_name)
    
    if result:
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
    else:
        _enviar(f"❌ Equipo '{team_name}' no encontrado.")


def _procesar_comando_avatar_random():
    """Procesa /avatar_random"""
    print("\\n→ Avatar random")
    result = get_avatar_prompt()
    
    if result:
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
    else:
        _enviar("❌ No hay prompts disponibles")


def _procesar_comando_avatar_today():
    """Procesa /avatar_today"""
    print("\\n→ Avatar today (5 prompts)")
    results = get_today_avatars(5)
    
    if not results:
        _enviar("❌ No hay prompts disponibles")
        return
    
    _enviar(f"📋 <b>5 Avatares del día:</b>\\n\\n{len(results)} prompts listos.")
    
    for i, result in enumerate(results, 1):
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = f"<b>Avatar {i}/5:</b>\\n\\n" + format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
        time.sleep(0.5)

'''

# Buscar posición de inserción
pos = contenido.find(insertar_antes)
if pos == -1:
    print("❌ No se encontró punto de inserción")
    exit(1)

# Insertar código
contenido_nuevo = contenido[:pos] + codigo_avatar + "\n\n" + contenido[pos:]

# Buscar el bucle main y agregar comandos
bucle_main = "for upd in res.get(\"result\", []):"
pos_bucle = contenido_nuevo.find(bucle_main)

if pos_bucle == -1:
    print("❌ No se encontró bucle principal")
    exit(1)

# Buscar dónde agregar los comandos (después de /video)
comandos_insert = '''
                # Comandos /avatar_prompt [team]
                if lower.startswith("/avatar_prompt "):
                    team_name = texto.split(" ", 1)[1].strip()
                    _procesar_comando_avatar_prompt(team_name)
                    continue

                # Comando /avatar_random
                if lower in ("/avatar_random", "/avatar"):
                    _procesar_comando_avatar_random()
                    continue

                # Comando /avatar_today
                if lower in ("/avatar_today", "/avatars"):
                    _procesar_comando_avatar_today()
                    continue
'''

# Buscar donde insertar (después del bloque /video)
bloque_video = 'if lower.startswith("/video ") or lower.startswith("/v "):'
pos_video = contenido_nuevo.find(bloque_video)

if pos_video != -1:
    # Buscar el fin de ese bloque (próxima línea con "if" o similar)
    pos_fin_video = contenido_nuevo.find('\n                if texto.startswith("/")', pos_video)
    if pos_fin_video != -1:
        contenido_nuevo = (
            contenido_nuevo[:pos_fin_video] + 
            "\n" + comandos_insert + 
            contenido_nuevo[pos_fin_video:]
        )

# Guardar
with open('src/automation/bot_consultas.py', 'w') as f:
    f.write(contenido_nuevo)

print("✅ Comandos de avatar agregados al bot")