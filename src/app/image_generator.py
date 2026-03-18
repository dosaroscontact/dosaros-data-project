from PIL import Image, ImageDraw, ImageFont
import os
# Cargar las fuentes (dentro de la función generar_post_triples)
font_path_bold = "assets/SpaceGrotesk-Bold.ttf"
font_path_regular = "assets/Inter-Regular.ttf"

# Definir tamaños
fuente_titular = ImageFont.truetype(font_path_bold, 60)
fuente_datos = ImageFont.truetype(font_path_regular, 45)


def generar_post_triples(jugadores, output_path="post_instagram.png"):
    # Configuración basada en tu Guía de Estilos
    ancho, alto = 1080, 1080
    color_fondo = "#FFFFFF"       # Blanco (70%)
    color_texto = "#0D1321"       # Azul Profundo (20%)
    color_acento = "#B1005A"      # Magenta (2%)

    # 1. Crear lienzo
    img = Image.new('RGB', (ancho, alto), color=color_fondo)
    draw = ImageDraw.Draw(img)

    # 2. Añadir Logo (debe estar en la carpeta assets)
    try:
        logo = Image.open("assets/logo1.png").convert("RGBA").resize((200, 200))
        img.paste(logo, (50, 20), logo)
    except:
        draw.text((50, 50), "DOS AROS", fill=color_texto)

    # 3. Títulos y Datos
    draw.text((50, 250), "CAZADORES DE TRIPLES", fill=color_acento, font=fuente_titular)
       
    y_pos = 400
    for j in jugadores:
        texto = f"{j['nombre'].upper()} ({j['equipo']}): {j['triples']} TRIPLES"
        draw.text((100, y_pos), texto, fill=color_texto)
        y_pos += 120

    img.save(output_path)
    return output_path
    # Ejemplo dentro de image_generator.py
    font_titular = ImageFont.truetype("assets/SpaceGrotesk-Bold.ttf", 60)
    draw.text((50, 250), "CAZADORES DE TRIPLES", fill=color_acento, font=font_titular)