import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import aiplatform
from google.oauth2 import service_account

# Cargar .env
load_dotenv()

# Configurar Google Cloud
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print(f"📍 Project: {PROJECT_ID}")
print(f"📍 Credentials: {CREDENTIALS_PATH}\n")
def generate_image(prompt, output_filename):
    """Genera imagen usando Vertex AI Image Generation"""
    try:
        # Usar Imagen 3 para generar
        model = aiplatform.ImageGenerationModel("imagegeneration@006")
        
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            width=1080,
            height=1920,
            safety_filter_level="block_few",
            person_generation="allow_adult"
        )
        
        # Guardar imagen localmente
        output_path = f'/home/pi/assets/generated/{output_filename}'
        images[0].save(output_path)
        
        print(f"✅ {output_filename} generada")
        return output_path
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        return None

def generate_all_avatars():
    """Genera avatares para todos los prompts"""
    
    conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
    cursor = conn.cursor()
    
    # Obtener prompts
    prompts = cursor.execute('''
        SELECT id, team_name, scene_type, prompt_text
        FROM avatar_prompts
        WHERE image_url IS NULL
        ORDER BY team_name
    ''').fetchall()
    
    print(f"🎯 Generando {len(prompts)} imágenes...\n")
    
    generated = 0
    for prompt_id, team_name, scene_type, prompt_text in prompts:
        # Crear nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{team_name.replace(' ', '_')}_{scene_type}_{timestamp}.png"
        
        # Generar imagen
        image_path = generate_image(prompt_text, filename)
        
        if image_path:
            # Actualizar BBDD con ruta local
            cursor.execute(
                'UPDATE avatar_prompts SET image_url = ? WHERE id = ?',
                (image_path, prompt_id)
            )
            conn.commit()
            generated += 1
    
    conn.close()
    
    print(f"\n✅ {generated} imágenes generadas")

if __name__ == "__main__":
    print("🎨 Sistema de Generación de Avatares - Vertex AI\n")
    generate_all_avatars()