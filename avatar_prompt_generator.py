import sqlite3
import random
from datetime import datetime

# URLs base
AVATAR_URLS = {
    1: "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_1_standing_casual.png",
    2: "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_2_action_jump.png",
    3: "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_3_upper_body.png",
    4: "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_4_standing_gorro.png",
}

LOGO_URLS = {
    "transparent": "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoDosAros.png",
    "neon": "https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoLetrasAzul.png",
}

PROMPT_TEMPLATE = """A cinematic, ultra-realistic, photorealistic full-body render. 

AVATAR: Use the exact avatar from {AVATAR_URL} as the base reference. Maintain 100% identity consistency (face, beard, sunglasses, proportions).

POSE: {POSTURA}

OUTFIT: {VESTIMENTA}. Colors: Primary {PRIMARY_COLOR}, Secondary {SECONDARY_COLOR}, Tertiary {TERTIARY_COLOR}

SCENE: {DECORADO}. Cinematic lighting, realistic depth, warm tones.

LOGO: Include the Dos Aros logo from {LOGO_URL} naturally blended in the scene without modification.

RENDER: Ultra-realistic 3D, Pixar-quality, 8K, sharp focus, global illumination, PBR materials.

BACKGROUND: Solid chroma key green (#00FF00), perfectly uniform, no gradients.

FRAMING: Full body visible, centered, no cropping."""

def get_logo_url(scene_type):
    """Asigna logo según scene_type"""
    if scene_type in ['ELITE', 'STREET']:
        return LOGO_URLS['neon']
    else:
        return LOGO_URLS['transparent']

def generate_prompt(team_id, team_name, scene_type, postura, vestimenta, decorado):
    """Genera prompt dinámico para un equipo"""
    
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    cursor = conn.cursor()
    
    # Buscar colores del equipo
    colors = cursor.execute(
        'SELECT primary_color, secondary_color, tertiary_color FROM team_colors WHERE team_name = ?',
        (team_name,)
    ).fetchone()
    
    if not colors:
        print(f"⚠️ {team_name}: no tiene colores definidos")
        conn.close()
        return None
    
    primary, secondary, tertiary = colors
    
    # Seleccionar avatar aleatorio
    avatar_variant = random.choice([1, 2, 3, 4])
    avatar_url = AVATAR_URLS[avatar_variant]
    
    # Seleccionar logo según scene_type
    logo_url = get_logo_url(scene_type)
    
    # Reemplazar placeholders
    prompt = PROMPT_TEMPLATE.format(
        AVATAR_URL=avatar_url,
        POSTURA=postura,
        VESTIMENTA=vestimenta,
        PRIMARY_COLOR=primary,
        SECONDARY_COLOR=secondary,
        TERTIARY_COLOR=tertiary,
        DECORADO=decorado,
        LOGO_URL=logo_url
    )
    
    # Insertar en BBDD
    cursor.execute('''
        INSERT INTO avatar_prompts 
        (team_id, team_name, scene_type, avatar_variant, avatar_url, logo_url, prompt_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (team_id, team_name, scene_type, avatar_variant, avatar_url, logo_url, prompt))
    
    conn.commit()
    conn.close()
    
    return prompt

# TEST: generar 3 prompts de ejemplo
if __name__ == "__main__":
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    cursor = conn.cursor()
    
    # Limpiar tabla
    cursor.execute('DELETE FROM avatar_prompts')
    conn.commit()
    
    # Obtener TODOS los equipos con colores
    teams = cursor.execute('''
        SELECT a.id, a.team_name, a.scene_type, a.postura, a.vestimenta, a.decorado
        FROM avatar_teams a
        WHERE a.team_name IN (SELECT team_name FROM team_colors)
        ORDER BY a.team_name
    ''').fetchall()
    
    conn.close()
    
    generated = 0
    for team_id, team_name, scene_type, postura, vestimenta, decorado in teams:
        prompt = generate_prompt(team_id, team_name, scene_type, postura, vestimenta, decorado)
        if prompt:
            generated += 1
    
    # Verificar
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    count = conn.execute('SELECT COUNT(*) FROM avatar_prompts').fetchone()[0]
    conn.close()
    print(f"\n✅ {count} prompts generados en total")