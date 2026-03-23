"""
image_generator.py — Generador de imágenes tipo story Instagram para perlas de datos.

Uso directo (test):
    python src/processors/image_generator.py

Uso desde código:
    from src.processors.image_generator import generar_imagen_perla
    path = generar_imagen_perla(perla)
"""

import os
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ──────────────────────────────────────────────
# Rutas base (relativas a la raíz del proyecto)
# ──────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent.parent
AVATARS_DIR   = BASE_DIR / "assets" / "avatars"
LOGOS_DIR     = BASE_DIR / "assets" / "logos"
GENERATED_DIR = BASE_DIR / "assets" / "generated"

LOGO_PATH    = LOGOS_DIR / "logo_fondo_transparente_grande.png"
DEFAULT_AVATAR = AVATARS_DIR / "presenter" / "presenter_pizarra.jpg"

# ──────────────────────────────────────────────
# Dimensiones story Instagram
# ──────────────────────────────────────────────
W, H = 1080, 1920

# ──────────────────────────────────────────────
# Diccionario de colores por equipo
# ──────────────────────────────────────────────
COLORES_EQUIPO = {
    "LAL": (85,  37, 130),   # púrpura Lakers
    "BOS": (0,  122,  51),   # verde Celtics
    "CHI": (206, 17,  65),   # rojo Bulls
    "MIA": (152,  0,  46),   # rojo oscuro Heat
    "DEN": (13,  34,  64),   # azul marino Nuggets
    "CLE": (134,  0,  56),   # granate Cavaliers
    "DET": (0,   45,  98),   # azul Pistons
    "SAC": (91,  43, 130),   # púrpura Kings
    "UTA": (0,   43,  92),   # azul marino Jazz
    "DEFAULT": (20, 20, 30), # negro azulado
}

# ──────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────

def _color_equipo(codigo: str) -> tuple:
    """Devuelve el color RGB del equipo o el DEFAULT."""
    return COLORES_EQUIPO.get(codigo.upper(), COLORES_EQUIPO["DEFAULT"])


def _cargar_avatar(codigo: str) -> Image.Image | None:
    """Carga el avatar del equipo. Fallback a DEFAULT si no existe."""
    candidatos = [
        AVATARS_DIR / f"nba_{codigo.upper()}.PNG",
        AVATARS_DIR / f"nba_{codigo.upper()}.png",
        AVATARS_DIR / f"euro_{codigo.upper()}.PNG",
        AVATARS_DIR / f"euro_{codigo.upper()}.png",
    ]
    for path in candidatos:
        if path.exists():
            return Image.open(path).convert("RGBA")

    # Fallback al avatar DEFAULT
    if DEFAULT_AVATAR.exists():
        return Image.open(DEFAULT_AVATAR).convert("RGBA")

    print(f"  Aviso: no se encontró avatar para '{codigo}', sin avatar.")
    return None


def _eliminar_fondo_verde(img: Image.Image,
                           verde_ref=(0, 200, 0),
                           tolerancia=80,
                           recorte_inferior=80) -> Image.Image:
    """
    Chroma key simple: elimina píxeles cercanos al verde de fondo (green screen).
    Recorta recorte_inferior px de la parte inferior para eliminar el rombo de watermark.
    Devuelve imagen RGBA con fondo transparente.
    """
    import numpy as np
    img = img.convert("RGBA")

    # Recortar parte inferior para eliminar watermark (rombo blanco de Google)
    w, h = img.size
    img = img.crop((0, 0, w, h - recorte_inferior))

    arr = np.array(img)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    r0, g0, b0 = verde_ref

    mascara = (
        (g > 100) &
        (g.astype(int) > r.astype(int) + 30) &
        (g.astype(int) > b.astype(int) + 20) &
        (np.abs(r.astype(int) - r0) + np.abs(g.astype(int) - g0) + np.abs(b.astype(int) - b0) < tolerancia * 3)
    )
    arr[mascara, 3] = 0
    return Image.fromarray(arr, "RGBA")


def _fuente(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Carga fuente del sistema. Fallback a la fuente por defecto de Pillow."""
    candidatos_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial_Bold.ttf",
    ]
    candidatos_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    lista = candidatos_bold if bold else candidatos_regular
    for path in lista:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _texto_envuelto(draw: ImageDraw.Draw, texto: str, fuente, ancho_max: int) -> list[str]:
    """Divide el texto en líneas que quepan en ancho_max."""
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()
        bbox = draw.textbbox((0, 0), prueba, font=fuente)
        if bbox[2] - bbox[0] <= ancho_max:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas


# ──────────────────────────────────────────────
# Función principal
# ──────────────────────────────────────────────

def generar_imagen_perla(perla: dict) -> str:
    """
    Genera una imagen story 1080x1920px para una perla de datos.

    Args:
        perla: dict con claves:
            - equipo (str): código NBA/Euro, ej. 'LAL', 'BOS'
            - dato_principal (str): texto grande, ej. '36.4 PTS'
            - subtitulo (str): texto mediano, ej. 'Luka Doncic — 5 partidos seguidos'
            - contexto (str, opcional): texto pequeño adicional

    Returns:
        str: path absoluto de la imagen generada
    """
    equipo    = perla.get("equipo", "DEFAULT").upper()
    dato      = perla.get("dato_principal", "")
    subtitulo = perla.get("subtitulo", "")
    contexto  = perla.get("contexto", "")
    fecha     = perla.get("fecha", "")
    fuente    = perla.get("fuente", "@dos_aros")

    # ── 1. Fondo de color sólido ──────────────────────────────────────────
    color_fondo = _color_equipo(equipo)
    # Añadimos un degradado vertical sutil oscureciendo la parte inferior
    imagen = Image.new("RGBA", (W, H), color_fondo)
    degradado = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_deg  = ImageDraw.Draw(degradado)
    for y in range(H):
        alpha = int((y / H) * 120)   # de 0 a 120 de opacidad
        draw_deg.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    imagen = Image.alpha_composite(imagen, degradado)

    # ── 2. Avatar ─────────────────────────────────────────────────────────
    avatar = _cargar_avatar(equipo)
    if avatar:
        avatar = _eliminar_fondo_verde(avatar)

        # Escalar para que ocupe 60% del ancho, manteniendo proporción
        avatar_w = int(W * 0.62)
        ratio    = avatar_w / avatar.width
        avatar_h = int(avatar.height * ratio)

        # Si es muy alto, limitar a 90% del alto
        if avatar_h > int(H * 0.90):
            avatar_h = int(H * 0.90)
            ratio    = avatar_h / avatar.height
            avatar_w = int(avatar.width * ratio)

        avatar = avatar.resize((avatar_w, avatar_h), Image.LANCZOS)

        # Pegar en lado derecho, centrado verticalmente
        pos_x = W - avatar_w + 20          # ligero solapamiento al borde
        pos_y = (H - avatar_h) // 2
        imagen.paste(avatar, (pos_x, pos_y), avatar)

    # ── 3. Marco decorativo semitransparente (lado izquierdo) ─────────────
    draw = ImageDraw.Draw(imagen)

    margen      = 50
    marco_w     = int(W * 0.62)
    marco_h     = int(H * 0.60)
    marco_x     = margen
    marco_y     = int(H * 0.22)
    radio       = 30

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rounded_rectangle(
        [marco_x, marco_y, marco_x + marco_w, marco_y + marco_h],
        radius=radio,
        fill=(0, 0, 0, 160)
    )
    imagen = Image.alpha_composite(imagen, overlay)
    draw   = ImageDraw.Draw(imagen)

    # ── 4. Texto ──────────────────────────────────────────────────────────
    padding_texto = marco_x + 35
    ancho_texto   = marco_w - 70

    # Código de equipo (pequeño, arriba del marco)
    f_equipo = _fuente(52, bold=True)
    draw.text(
        (padding_texto, marco_y - 70),
        equipo,
        font=f_equipo,
        fill=(255, 255, 255, 200)
    )

    # Dato principal (grande)
    f_dato = _fuente(160, bold=True)
    lineas_dato = _texto_envuelto(draw, dato, f_dato, ancho_texto)
    y_cursor = marco_y + 35
    for linea in lineas_dato:
        draw.text((padding_texto, y_cursor), linea, font=f_dato, fill=(255, 255, 255, 255))
        bbox = draw.textbbox((0, 0), linea, font=f_dato)
        y_cursor += (bbox[3] - bbox[1]) + 10

    # Línea separadora
    y_cursor += 15
    draw.line([(padding_texto, y_cursor), (padding_texto + ancho_texto - 40, y_cursor)],
              fill=(255, 255, 255, 120), width=2)
    y_cursor += 25

    # Subtítulo (mediano)
    f_sub = _fuente(55, bold=False)
    lineas_sub = _texto_envuelto(draw, subtitulo, f_sub, ancho_texto)
    for linea in lineas_sub:
        draw.text((padding_texto, y_cursor), linea, font=f_sub, fill=(220, 220, 220, 230))
        bbox = draw.textbbox((0, 0), linea, font=f_sub)
        y_cursor += (bbox[3] - bbox[1]) + 8

    # Contexto (pequeño, opcional)
    if contexto:
        y_cursor += 10
        f_ctx = _fuente(38, bold=False)
        lineas_ctx = _texto_envuelto(draw, contexto, f_ctx, ancho_texto)
        for linea in lineas_ctx:
            draw.text((padding_texto, y_cursor), linea, font=f_ctx, fill=(180, 180, 180, 200))
            bbox = draw.textbbox((0, 0), linea, font=f_ctx)
            y_cursor += (bbox[3] - bbox[1]) + 6

    # Fecha y fuente (tercer bloque, abajo del marco)
    if fecha or fuente:
        y_cursor += 18
        draw.line([(padding_texto, y_cursor), (padding_texto + ancho_texto - 40, y_cursor)],
                  fill=(255, 255, 255, 60), width=1)
        y_cursor += 14
        f_pie = _fuente(36, bold=False)
        pie_texto = " · ".join(filter(None, [fecha, fuente]))
        draw.text((padding_texto, y_cursor), pie_texto, font=f_pie, fill=(160, 160, 160, 200))

    # ── 5. Logo en esquina inferior izquierda (invertido a blanco) ───────────
    if LOGO_PATH.exists():
        try:
            import numpy as np
            logo = Image.open(LOGO_PATH).convert("RGBA")

            # Invertir canales RGB para pasar de azul oscuro a blanco
            arr_logo = np.array(logo)
            arr_logo[:, :, :3] = 255 - arr_logo[:, :, :3]
            logo = Image.fromarray(arr_logo, "RGBA")

            # Redimensionar a 200px de ancho manteniendo proporción
            logo_w = 200
            ratio_logo = logo_w / logo.width
            logo_h = int(logo.height * ratio_logo)
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

            pos_logo_x = 40
            pos_logo_y = H - logo_h - 40
            imagen.paste(logo, (pos_logo_x, pos_logo_y), logo)
        except Exception as e:
            print(f"  Aviso: no se pudo cargar el logo: {e}")
    else:
        print(f"  Aviso: logo no encontrado en {LOGO_PATH}")

    # ── 6. Guardar imagen ─────────────────────────────────────────────────
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre    = f"imagen_{fecha_str}_{equipo}.png"
    path_out  = GENERATED_DIR / nombre

    imagen_final = imagen.convert("RGB")
    imagen_final.save(str(path_out), "PNG", quality=95)
    print(f"  Imagen generada: {path_out}")
    return str(path_out)


# ──────────────────────────────────────────────
# Test
# ──────────────────────────────────────────────

if __name__ == "__main__":
    perla_test = {
        "equipo": "LAL",
        "dato_principal": "36.4 PTS",
        "subtitulo": "Luka Doncic — 5 partidos seguidos anotando 35+",
        "contexto": "Mejor racha anotadora de la temporada",
        "fecha": "23 Mar 2026",
        "fuente": "@dos_aros"
    }
    print("Generando imagen de test...")
    path = generar_imagen_perla(perla_test)
    print(f"Listo: {path}")
