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
FONTS_DIR     = BASE_DIR / "assets" / "static"

LOGO_PATH    = LOGOS_DIR / "logo_fondo_transparente_grande.png"
DEFAULT_AVATAR = AVATARS_DIR / "presenter" / "presenter_pizarra.jpg"

# ──────────────────────────────────────────────
# Dimensiones story Instagram
# ──────────────────────────────────────────────
W, H = 1080, 1920

# ──────────────────────────────────────────────
# Diccionario de colores por equipo (RGB)
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
# Descripciones de camiseta para Google ImageFX
# Cubre los 30 equipos NBA + 20 Euroliga
# ──────────────────────────────────────────────
# NBA: 30 equipos (clave = código oficial NBA)
TEAM_JERSEY_COLORS = {
    "ATL": "red and gold Atlanta Hawks jersey, number 7",
    "BOS": "green and white Boston Celtics jersey, number 7",
    "BKN": "black and white Brooklyn Nets jersey, number 7",
    "CHA": "purple and teal Charlotte Hornets jersey, number 7",
    "CHI": "red and black Chicago Bulls jersey, number 7",
    "CLE": "wine and gold Cleveland Cavaliers jersey, number 7",
    "DAL": "blue and silver Dallas Mavericks jersey, number 7",
    "DEN": "navy and gold Denver Nuggets jersey, number 7",
    "DET": "blue and red Detroit Pistons jersey, number 7",
    "GSW": "royal blue and gold Golden State Warriors jersey, number 7",
    "HOU": "red and silver Houston Rockets jersey, number 7",
    "IND": "blue and gold Indiana Pacers jersey, number 7",
    "LAC": "red and blue LA Clippers jersey, number 7",
    "LAL": "purple and gold Los Angeles Lakers jersey, number 7",
    "MEM": "navy and gold Memphis Grizzlies jersey, number 7",
    "MIA": "black and red Miami Heat jersey, number 7",
    "MIL": "green and cream Milwaukee Bucks jersey, number 7",
    "MIN": "blue and green Minnesota Timberwolves jersey, number 7",
    "NOP": "navy and gold New Orleans Pelicans jersey, number 7",
    "NYK": "blue and orange New York Knicks jersey, number 7",
    "OKC": "blue and orange Oklahoma City Thunder jersey, number 7",
    "ORL": "blue and black Orlando Magic jersey, number 7",
    "PHI": "blue and red Philadelphia 76ers jersey, number 7",
    "PHX": "purple and orange Phoenix Suns jersey, number 7",
    "POR": "red and black Portland Trail Blazers jersey, number 7",
    "SAC": "purple and silver Sacramento Kings jersey, number 7",
    "SAS": "black and silver San Antonio Spurs jersey, number 7",
    "TOR": "red and black Toronto Raptors jersey, number 7",
    "UTA": "navy and gold Utah Jazz jersey, number 7",
    "WAS": "blue and red Washington Wizards jersey, number 7",
    "DEFAULT": "black t-shirt with bold red number 7, diagonal red-white-red stripe, Dos Aros brand",
}

# Euroliga: 20 equipos (clave = código oficial Euroliga API)
# MIL aquí es EA7 Milan — distinto al MIL de NBA (Milwaukee Bucks)
EURO_JERSEY_COLORS = {
    "ASV": "blue and yellow LDLC ASVEL jersey, number 7",
    "BAR": "blue and red FC Barcelona jersey, number 7",
    "BAS": "blue and red Baskonia jersey, number 7",
    "DUB": "black and gold Dubai Basketball jersey, number 7",
    "HTA": "red and black Hapoel Tel Aviv jersey, number 7",
    "IST": "blue and white Anadolu Efes jersey, number 7",
    "MAD": "white and gold Real Madrid jersey, number 7",
    "MCO": "red and white AS Monaco jersey, number 7",
    "MIL": "white and red EA7 Milan jersey, number 7",
    "MUN": "red and white Bayern Munich jersey, number 7",
    "OLY": "red and white Olympiacos jersey, number 7",
    "PAM": "black and orange Valencia Basket jersey, number 7",
    "PAN": "green and black Panathinaikos jersey, number 7",
    "PAR": "black and white Partizan Belgrade jersey, number 7",
    "PRS": "blue and red Paris Basketball jersey, number 7",
    "RED": "red and white Crvena Zvezda Belgrade jersey, number 7",
    "TEL": "yellow and blue Maccabi Tel Aviv jersey, number 7",
    "ULK": "yellow and navy Fenerbahce Beko jersey, number 7",
    "VIR": "black and white Virtus Bologna jersey, number 7",
    "ZAL": "green and white Zalgiris Kaunas jersey, number 7",
    "DEFAULT": "black t-shirt with bold red number 7, diagonal red-white-red stripe, Dos Aros brand",
}

# Alias para compatibilidad con código previo
JERSEYS_IMAGEFX = TEAM_JERSEY_COLORS

# ──────────────────────────────────────────────
# Posturas recomendadas por tipo de perla
# ──────────────────────────────────────────────
POSTURAS_IMAGEFX = {
    "explosion_anotadora": "celebrating with both arms raised high, triumphant expression",
    "rebotes":             "athletic crouching stance, arms outstretched ready to grab a rebound",
    "defensa":             "athletic crouching defensive stance, low center of gravity, intense focus",
    "triple_doble":        "surprised reaction pose, hands on head, wide eyes, amazed expression",
    "record":              "presenter pointing to a stats board with one hand, confident smile",
    "record_personal":     "presenter pointing to a stats board with one hand, confident smile",
    "equipo":              "arms spread wide celebrating, team pride gesture",
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
    """
    Carga fuente del sistema con fallback progresivo.
    Prioriza Raspberry Pi (DejaVu/Liberation/FreeSans) antes que Windows/Mac.
    """
    candidatos_bold = [
        # Bundled en el repo (funciona en cualquier SO sin instalación)
        str(FONTS_DIR / "SpaceGrotesk-Bold.ttf"),
        str(FONTS_DIR / "Inter_28pt-Bold.ttf"),
        str(FONTS_DIR / "Inter_18pt-Bold.ttf"),
        # Raspberry Pi / Debian / Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial_Bold.ttf",
    ]
    candidatos_regular = [
        # Bundled en el repo
        str(FONTS_DIR / "SpaceGrotesk-Regular.ttf"),
        str(FONTS_DIR / "Inter_28pt-Regular.ttf"),
        str(FONTS_DIR / "Inter_18pt-Regular.ttf"),
        # Raspberry Pi / Debian / Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
    ]
    lista = candidatos_bold if bold else candidatos_regular
    for path in lista:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                print(f"  [fuente] Cargada: {path} size={size}")
                return font
            except Exception as e:
                print(f"  [fuente] Fallo {path}: {e}")
                continue

    # Fallback: load_default con size si Pillow >= 10, si no sin size
    print(f"  [fuente] FALLBACK load_default size={size} (texto puede ser pequeño)")
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _ancho_texto(draw: ImageDraw.Draw, texto: str, fuente) -> int:
    """Devuelve el ancho en px del texto con la fuente dada. Robusto ante bitmap fonts."""
    try:
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        return bbox[2] - bbox[0]
    except Exception:
        # Bitmap font: estimación aproximada (10px por carácter)
        return len(texto) * 10


def _alto_texto(draw: ImageDraw.Draw, texto: str, fuente) -> int:
    """Devuelve el alto en px del texto con la fuente dada."""
    try:
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        return bbox[3] - bbox[1]
    except Exception:
        return 16


def _texto_envuelto(draw: ImageDraw.Draw, texto: str, fuente, ancho_max: int) -> list[str]:
    """Divide el texto en líneas que quepan en ancho_max."""
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()
        if _ancho_texto(draw, prueba, fuente) <= ancho_max:
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
    padding_texto = marco_x + 35      # coordenada X absoluta dentro del lienzo
    ancho_texto   = marco_w - 70
    print(f"  [texto] marco: x={marco_x} y={marco_y} w={marco_w} h={marco_h}")
    print(f"  [texto] padding_x={padding_texto} ancho_max={ancho_texto}")

    # Código de equipo (pequeño, arriba del marco)
    f_equipo = _fuente(52, bold=True)
    x_eq, y_eq = padding_texto, marco_y - 70
    print(f"  [texto] DEBUG: dibujando equipo '{equipo}' en ({x_eq}, {y_eq})")
    draw.text((x_eq, y_eq), equipo, font=f_equipo, fill=(255, 255, 255, 200))
    print(f"  [texto] Texto dibujado: '{equipo}' en {x_eq},{y_eq}")

    # Dato principal (grande)
    f_dato  = _fuente(160, bold=True)
    y_cursor = marco_y + 35
    lineas_dato = _texto_envuelto(draw, dato, f_dato, ancho_texto)
    print(f"  [texto] dato_principal='{dato}' -> {len(lineas_dato)} lineas")
    for linea in lineas_dato:
        print(f"  [texto] DEBUG: dibujando dato '{linea}' en ({padding_texto}, {y_cursor})")
        draw.text((padding_texto, y_cursor), linea, font=f_dato, fill=(255, 255, 255, 255))
        alto = _alto_texto(draw, linea, f_dato)
        print(f"  [texto] Texto dibujado: '{linea}' en {padding_texto},{y_cursor} alto={alto}")
        y_cursor += alto + 10

    # Línea separadora
    y_cursor += 15
    draw.line([(padding_texto, y_cursor), (padding_texto + ancho_texto - 40, y_cursor)],
              fill=(255, 255, 255, 120), width=2)
    y_cursor += 25

    # Subtítulo (mediano)
    f_sub = _fuente(55, bold=False)
    lineas_sub = _texto_envuelto(draw, subtitulo, f_sub, ancho_texto)
    print(f"  [texto] subtitulo='{subtitulo}' -> {len(lineas_sub)} lineas")
    for linea in lineas_sub:
        print(f"  [texto] DEBUG: dibujando subtitulo '{linea}' en ({padding_texto}, {y_cursor})")
        draw.text((padding_texto, y_cursor), linea, font=f_sub, fill=(220, 220, 220, 230))
        alto = _alto_texto(draw, linea, f_sub)
        print(f"  [texto] Texto dibujado: '{linea}' en {padding_texto},{y_cursor} alto={alto}")
        y_cursor += alto + 8

    # Contexto (pequeño, opcional)
    if contexto:
        y_cursor += 10
        f_ctx = _fuente(38, bold=False)
        lineas_ctx = _texto_envuelto(draw, contexto, f_ctx, ancho_texto)
        print(f"  [texto] contexto='{contexto}' -> {len(lineas_ctx)} lineas")
        for linea in lineas_ctx:
            print(f"  [texto] DEBUG: dibujando contexto '{linea}' en ({padding_texto}, {y_cursor})")
            draw.text((padding_texto, y_cursor), linea, font=f_ctx, fill=(180, 180, 180, 200))
            alto = _alto_texto(draw, linea, f_ctx)
            print(f"  [texto] Texto dibujado: '{linea}' en {padding_texto},{y_cursor} alto={alto}")
            y_cursor += alto + 6

    # Fecha y fuente (pie, abajo del marco)
    if fecha or fuente:
        y_cursor += 18
        draw.line([(padding_texto, y_cursor), (padding_texto + ancho_texto - 40, y_cursor)],
                  fill=(255, 255, 255, 60), width=1)
        y_cursor += 14
        f_pie     = _fuente(36, bold=False)
        pie_texto = " · ".join(filter(None, [fecha, fuente]))
        print(f"  [texto] DEBUG: dibujando pie '{pie_texto}' en ({padding_texto}, {y_cursor})")
        draw.text((padding_texto, y_cursor), pie_texto, font=f_pie, fill=(160, 160, 160, 200))
        print(f"  [texto] Texto dibujado: '{pie_texto}' en {padding_texto},{y_cursor}")

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
# Prompt para Google ImageFX
# ──────────────────────────────────────────────

def generar_prompt_imagefx(perla: dict, imagen_pillow_path: str) -> str:
    """
    Genera un prompt listo para pegar en Google ImageFX.

    Args:
        perla             : dict de la perla (claves: equipo, tipo, jugador,
                            dato_principal o stat_clave+valor, razon)
        imagen_pillow_path: path de la imagen Pillow generada (referencia visual)

    Returns:
        str con el prompt completo para Google ImageFX
    """
    equipo = str(perla.get("equipo", "DEFAULT")).upper()

    # Dato que aparece en la imagen Pillow
    if perla.get("dato_principal"):
        dato = perla["dato_principal"]
    else:
        stat  = perla.get("stat_clave", "")
        valor = perla.get("valor", "")
        dato  = f"{valor} {stat}".strip() if (stat or valor) else perla.get("razon", "")

    # Tipo → postura
    tipo    = str(perla.get("tipo", "DEFAULT")).lower()
    postura = POSTURAS_IMAGEFX.get(tipo, "standing at a basketball analytics whiteboard, pointer in hand")

    # Camiseta: usa EURO_JERSEY_COLORS si la liga es Euroliga, si no NBA
    liga = str(perla.get("liga", "")).upper()
    color_dict = EURO_JERSEY_COLORS if liga == "EUROLIGA" else TEAM_JERSEY_COLORS
    jersey = color_dict.get(equipo, TEAM_JERSEY_COLORS["DEFAULT"])

    # Avatar de referencia
    avatar_path = str(AVATARS_DIR / f"nba_{equipo}.PNG")

    prompt = (
        f"Basketball analytics presenter character based on the reference avatar attached. "
        f"The character is wearing a {jersey}. "
        f"The Dos Aros logo is clearly visible on the left chest of the jersey. "
        f"The character is {postura}. "
        f"A large screen or holographic display behind the character shows the stat: \"{dato}\". "
        f"Professional NBA arena background with dramatic spotlights. "
        f"Photorealistic, cinematic quality, vibrant colors, 9:16 vertical format."
    )

    print(f"  Avatar referencia: {avatar_path}")
    print(f"  Imagen Pillow    : {imagen_pillow_path}")
    return prompt


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
