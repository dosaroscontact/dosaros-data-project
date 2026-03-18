from PIL import Image, ImageDraw, ImageFont
import os

def generar_post_triples(jugadores, output_path="post_instagram.png"):
    # Paleta de colores - Guía de Estilo Dos Aros
    ancho, alto = 1080, 1080
    color_fondo = "#FFFFFF"       # 70% Blanco
    color_texto = "#0D1321"       # 20% Azul Profundo
    color_acento = "#B1005A"      # 2% Magenta Oscuro
    color_lineas = "#E6E8EE"      # 7% Gris Analítico

    # 1. Crear lienzo
    img = Image.new('RGB', (ancho, alto), color=color_fondo)
    draw = ImageDraw.Draw(img)

    # 2. Cargar Fuentes (Rutas corregidas)
    # Usamos las versiones Variable que están en la raíz de assets/
    font_bold = "assets/SpaceGrotesk-VariableFont_wght.ttf"
    font_regular = "assets/Inter-VariableFont_opsz,wght.ttf"

    try:
        fuente_titular = ImageFont.truetype(font_bold, 70)
        fuente_subtitulo = ImageFont.truetype(font_bold, 35)
        fuente_datos = ImageFont.truetype(font_regular, 45)
    except Exception as e:
        print(f"⚠️ Error cargando fuentes: {e}. Usando fuente por defecto.")
        fuente_titular = fuente_subtitulo = fuente_datos = ImageFont.load_default()

    # 3. Diseño: Cabecera y Logo
    try:
        # Probamos con logo2.png que suele ser el más limpio para fondos blancos
        logo = Image.open("assets/logo2.png").convert("RGBA").resize((180, 180))
        img.paste(logo, (50, 40), logo)
    except:
        draw.text((50, 50), "DOS AROS", fill=color_texto, font=fuente_titular)

    # Título de la sección
    draw.text((50, 260), "CAZADORES DE TRIPLES", fill=color_acento, font=fuente_subtitulo)
    draw.line([(50, 310), (1030, 310)], fill=color_lineas, width=3)

    # 4. Listado de Jugadores
    y_pos = 400
    for j in jugadores:
        # Nombre del jugador
        draw.text((80, y_pos), j['nombre'].upper(), fill=color_texto, font=fuente_datos)
        
        # El dato (triples) alineado a la derecha
        dato_texto = f"{j['triples']} 🎯"
        # Calculamos ancho para alinear (aprox)
        draw.text((850, y_pos), dato_texto, fill=color_texto, font=fuente_datos)
        
        # Línea sutil de separación
        draw.line([(80, y_pos + 80), (1000, y_pos + 80)], fill=color_lineas, width=1)
        y_pos += 150

    # 5. Pie de Página (Insight)
    draw.rectangle([0, 950, 1080, 1080], fill=color_texto)
    insight_text = "ANÁLISIS: Volumen de tiro exterior por encima de la media de temporada."
    draw.text((50, 990), insight_text, fill="#FFFFFF", font=fuente_subtitulo)

    # Guardar resultado
    img.save(output_path)
    return output_path