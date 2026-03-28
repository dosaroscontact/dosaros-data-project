"""
populate_avatars.py — Crea e inserta toda la configuración de equipos y
parámetros de avatar en la base de datos.

Tablas:
  teams_metadata  — equipos NBA + EuroLeague con colores oficiales
  dim_posturas    — catálogo de posturas del avatar
  dim_vestimentas — catálogo de vestimentas
  dim_decorados   — catálogo de decorados/entornos
  dim_tipos_logo  — catálogo de tipos de integración del logo

Uso:
    python src/database/populate_avatars.py

Generador de prompts SQL de ejemplo:
    SELECT 'Un jugador de los ' || name ||
           ' con colores ' || color_primary || ' y ' || color_secondary ||
           '. Postura: ' || (SELECT valor FROM dim_posturas ORDER BY RANDOM() LIMIT 1) ||
           '. Vestimenta: ' || (SELECT valor FROM dim_vestimentas ORDER BY RANDOM() LIMIT 1) ||
           '. Decorado: ' || (SELECT valor FROM dim_decorados ORDER BY RANDOM() LIMIT 1) ||
           '. Logo: ' || (SELECT valor FROM dim_tipos_logo ORDER BY RANDOM() LIMIT 1)
    FROM teams_metadata ORDER BY RANDOM() LIMIT 1;
"""

import os
import sqlite3

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# ──────────────────────────────────────────────────────────────────────────────
# DDL — Crear tablas
# ──────────────────────────────────────────────────────────────────────────────

DDL = """
CREATE TABLE IF NOT EXISTS teams_metadata (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    code           TEXT    NOT NULL UNIQUE,
    name           TEXT    NOT NULL,
    liga           TEXT    NOT NULL,
    color_primary  TEXT,
    color_secondary TEXT,
    color_accent   TEXT,
    color_extra    TEXT
);

CREATE TABLE IF NOT EXISTS dim_posturas (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_vestimentas (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_decorados (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_tipos_logo (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT NOT NULL UNIQUE
);
"""

# ──────────────────────────────────────────────────────────────────────────────
# Equipos NBA — 30 equipos con colores oficiales
# ──────────────────────────────────────────────────────────────────────────────
# (code, name, color_primary, color_secondary, color_accent, color_extra)

NBA = [
    ("ATL", "Atlanta Hawks",           "Rojo",             "Blanco",      "Verde Volt",     None),
    ("BOS", "Boston Celtics",          "Verde Trébol",     "Blanco",      "Oro",            None),
    ("BKN", "Brooklyn Nets",           "Negro",            "Blanco",      "Gris",           None),
    ("CHA", "Charlotte Hornets",       "Púrpura",          "Teal",        "Oro",            None),
    ("CHI", "Chicago Bulls",           "Rojo Toro",        "Negro",       "Blanco",         None),
    ("CLE", "Cleveland Cavaliers",     "Granate",          "Oro",         "Azul Marino",    None),
    ("DAL", "Dallas Mavericks",        "Azul Mavericks",   "Azul Marino", "Plata",          None),
    ("DEN", "Denver Nuggets",          "Azul Medianoche",  "Amarillo Sol","Rojo Plano",     None),
    ("DET", "Detroit Pistons",         "Azul",             "Rojo",        "Blanco",         None),
    ("GSW", "Golden State Warriors",   "Azul Real",        "Amarillo California", "Blanco", None),
    ("HOU", "Houston Rockets",         "Rojo",             "Plata",       "Blanco",         None),
    ("IND", "Indiana Pacers",          "Azul Marino",      "Oro",         "Plata",          None),
    ("LAC", "LA Clippers",             "Azul",             "Rojo",        "Blanco",         None),
    ("LAL", "Los Angeles Lakers",      "Púrpura",          "Oro",         "Blanco",         None),
    ("MEM", "Memphis Grizzlies",       "Azul Grizzly",     "Azul Cielo",  "Oro",            None),
    ("MIA", "Miami Heat",              "Rojo Fuego",       "Negro",       "Blanco",         "Rosa Vice"),
    ("MIL", "Milwaukee Bucks",         "Verde Bosque",     "Crema",       "Azul",           None),
    ("MIN", "Minnesota Timberwolves",  "Azul Medianoche",  "Verde Aurora","Gris",           None),
    ("NOP", "New Orleans Pelicans",    "Azul Marino",      "Oro",         "Rojo",           None),
    ("NYK", "New York Knicks",         "Azul Knicks",      "Naranja Knicks","Plata",        None),
    ("OKC", "Oklahoma City Thunder",   "Azul Celeste",     "Naranja",     "Amarillo",       None),
    ("ORL", "Orlando Magic",           "Azul",             "Negro",       "Plata",          None),
    ("PHI", "Philadelphia 76ers",      "Azul Real",        "Rojo",        "Blanco",         "Oro"),
    ("PHX", "Phoenix Suns",            "Púrpura",          "Naranja",     "Oro",            None),
    ("POR", "Portland Trail Blazers",  "Rojo",             "Negro",       "Blanco",         None),
    ("SAC", "Sacramento Kings",        "Púrpura",          "Plata",       "Negro",          None),
    ("SAS", "San Antonio Spurs",       "Plata Metálico",   "Negro",       "Blanco",         None),
    ("TOR", "Toronto Raptors",         "Rojo Raptors",     "Negro",       "Plata",          None),
    ("UTA", "Utah Jazz",               "Azul Marino",      "Oro",         "Blanco",         None),
    ("WAS", "Washington Wizards",      "Azul Marino",      "Rojo",        "Blanco",         None),
]

# ──────────────────────────────────────────────────────────────────────────────
# Equipos EuroLeague
# ──────────────────────────────────────────────────────────────────────────────

EURO = [
    ("MAD", "Real Madrid",             "Blanco",     "Púrpura Real", "Oro",      None),
    ("TEL", "Maccabi Tel Aviv",        "Amarillo",   "Azul",         "Oro",      None),
    ("CSK", "CSKA Moscow",             "Rojo",       "Azul",         "Oro",      None),
    ("OLY", "Olympiacos Piraeus",      "Rojo",       "Blanco",       "Negro",    None),
    ("JUG", "Jugoplastika Split",      "Amarillo",   "Negro",        "Blanco",   None),
    ("BAR", "FC Barcelona",            "Azul",       "Grana",        "Amarillo", None),
    ("PAN", "Panathinaikos AKTOR",     "Verde",      "Blanco",       "Oro",      None),
    ("VIR", "Virtus Segafredo Bologna","Blanco",     "Negro",        "Oro",      None),
    ("ZAL", "Zalgiris Kaunas",         "Verde",      "Blanco",       "Negro",    None),
    ("PAR", "Partizan Belgrade",       "Negro",      "Blanco",       "Plata",    None),
    ("LIM", "Limoges CSP",             "Amarillo",   "Verde",        "Blanco",   None),
    ("IST", "Anadolu Efes",            "Azul Efes",  "Blanco",       "Rojo",     None),
    ("ULK", "Fenerbahçe Beko",         "Azul Marino","Amarillo",     "Blanco",   None),
    ("MCO", "AS Monaco",               "Rojo",       "Blanco",       "Negro",    None),
    ("MIL", "EA7 Emporio Armani Milano","Blanco",    "Rojo",         "Negro",    None),
    ("MUN", "FC Bayern Munich",        "Rojo",       "Blanco",       "Azul Bavaria", None),
    ("ASV", "LDLC ASVEL",              "Azul",       "Amarillo",     "Blanco",   None),
    ("BAS", "TD Systems Baskonia",     "Azul",       "Rojo",         "Blanco",   None),
    ("DUB", "Dubai Basketball",        "Negro",      "Oro",          "Blanco",   None),
    ("HTA", "Hapoel Tel Aviv",         "Rojo",       "Negro",        "Blanco",   None),
    ("PAM", "Valencia Basket",         "Negro",      "Naranja",      "Blanco",   None),
    ("PRS", "Paris Basketball",        "Azul",       "Rojo",         "Blanco",   None),
    ("RED", "Crvena Zvezda mts",       "Rojo",       "Blanco",       "Azul",     None),
    ("CIB", "Cibona Zagreb",           "Azul",       "Blanco",       "Plata",    None),
]

# ──────────────────────────────────────────────────────────────────────────────
# Dimensiones
# ──────────────────────────────────────────────────────────────────────────────

POSTURAS = [
    "De pie, cruzado de brazos, actitud serena y confiada",
    "Sentado en el suelo de una pista interior, sujetando un balón con una mano",
    "De pie, mirando hacia un lado, con un pie apoyado en una caja",
    "Caminando hacia la cámara por un túnel de estadio",
    "De pie, con las manos en los bolsillos de la chaqueta",
    "De pie, de espaldas a cámara, mirando por una ventana grande",
    "Sentado en un banco metálico, pensativo",
    "De pie en una pose de hype total, con los brazos abiertos",
    "Sentado en un sofá de cuero moderno con un balón en la mano",
    "De pie con un pie sobre una silla, mirando a cámara con confianza",
    "En posición de defensa baja deslizándose lateralmente",
    "Saltando para un rebote con los dos brazos completamente extendidos",
    "Rugiendo tras un tapón espectacular con los puños cerrados",
    "Flexionando los músculos con expresión intensa tras un mate",
    "Mirando fijamente a cámara con intensidad gélida",
    "Haciendo el gesto de silencio con el dedo índice en los labios",
    "Botando el balón entre las piernas con velocidad y control",
    "Preparado para salir en contraataque con expresión eléctrica",
    "Lanzando un triple desde la esquina con forma perfecta",
    "Saltando para un tapón espectacular",
    "Lanzando un tiro libre con máxima concentración",
    "De pie con actitud desafiante, mirada directa a cámara",
    "En el aire realizando un mate explosivo",
    "Defendiendo con los brazos extendidos en posición baja",
    "Realizando un pase de pecho con fuerza y precisión",
    "Señalando al cielo con el índice tras anotar un triple",
    "Caminando por una alfombra roja con un balón bajo el brazo",
    "Apoyado en una palmera con un balón de fuego en la mano",
    "De pie en una pose majestuosa y elegante, ligeramente elevado",
    "De pie, apoyado en un coche deportivo moderno con actitud",
    "Sentado en una moto tipo scooter moderna con actitud",
    "De pie en una pose dinámica con un salto sutil del suelo",
    "De pie con una pose de modelo, mirando a cámara con confianza",
    "Sentado en un sillón de diseño futurista con una tablet",
    "De pie en pose de acción, simulando un lanzamiento explosivo",
    "De pie con una pose seria y minimalista, inmóvil como una estatua",
    "Sentado en una silla de diseño clásico italiano con elegancia",
    "De pie en una pose relajada con los brazos cruzados naturalmente",
    "Firme, con una mirada gélida y profesional en posición de guardia",
    "En posición de triple amenaza, concentrado y listo para atacar",
    "Botando el balón con elegancia y control, mirada perdida en el horizonte",
    "Entrando a canasta con una bandeja fluida y elegante",
    "Levantando el puño en señal de victoria con mirada intensa",
    "Defendiendo intensamente con las manos bajas en posición de alerta",
    "Atrapando un rebote con fuerza y determinación en el aire",
    "Gritando de emoción tras un triple decisivo en el último segundo",
    "Lanzando un tiro de media distancia con forma técnica perfecta",
    "Sosteniendo un trofeo con ambas manos sobre la cabeza",
    "De pie ante el skyline de la ciudad con actitud de campeón",
    "Preparado para el despegue, rodilla elevada en pose dinámica",
]

VESTIMENTAS = [
    "Camiseta de baloncesto de juego oficial",
    "Chaqueta de chándal retro con franjas en los laterales",
    "Sudadera con capucha estilizada de corte moderno",
    "Pantalones de chándal y camiseta técnica ajustada",
    "Chaqueta bomber elegante y moderna con parches",
    "Camiseta de baloncesto edición Vice con degradados de color",
    "Sudadera sin mangas con capucha",
    "Cortavientos técnico de estilo urbano con cremallera lateral",
    "Polo deportivo de alta calidad con bordado en el pecho",
    "Camiseta de baloncesto de manga corta estilizada con detalles",
    "Camiseta con líneas verticales finas estilo pinstripes",
    "Equipación moderna con tipografía náutica y detalles marineros",
    "Sudadera oversize con el logo del equipo en el pecho",
    "Camiseta con detalles en color crema edición City Edition",
    "Chaqueta técnica reflectante de entrenamiento nocturno",
    "Camiseta con detalles de carnaval y lentejuelas doradas",
    "Camiseta clásica con cuello redondo y número en el pecho",
    "Equipación con rayos eléctricos en los laterales",
    "Camiseta con estrellas metálicas impresas en los laterales",
    "Camiseta de estilo histórico con estrellas bordadas",
    "Equipación oficial con detalles en verde neón fluorescente",
    "Camiseta clásica de tirantes con número en el pecho",
    "Sudadera sin mangas con capucha y estampado minimalista",
    "Camiseta de entrenamiento técnica con detalles del equipo",
    "Camiseta de manga corta de compresión de alto rendimiento",
    "Camiseta con el diseño del arcoíris retro de los 70",
    "Chaqueta de calentamiento moderna con cremallera completa",
    "Camiseta de tirantes con detalles dorados y lentejuelas",
    "Chaqueta de traje de lino de diseño italiano",
    "Camiseta técnica de running de alta gama",
    "Chaqueta de cuero estilo biker con tachuelas en los hombros",
    "Conjunto de chándal completo moderno",
    "Camisa de seda estampada de lujo",
    "Suéter de punto de alta calidad con cuello vuelto",
    "Pantalones cortos de baloncesto y camiseta interior técnica",
    "Sudadera con capucha de algodón pesado heavyweight",
    "Chaqueta blazer desestructurada",
    "Parka técnica de estilo urbano con forro interior visible",
    "Chándal de entrenamiento de alta gama",
    "Camiseta técnica con detalles geométricos",
    "Equipación retro de los años 80 con nombre en el pecho",
    "Camiseta negra con la V blanca característica",
    "Camiseta técnica con patrones inspirados en el paisaje local",
    "Camiseta negra sobria con detalles geométricos en blanco",
    "Equipación clásica de los años 90",
    "Chaqueta de trabajo técnica con detalles metálicos",
    "Traje negro de lujo con detalles en hilo dorado",
    "Cortavientos técnico con el logo en el pecho",
    "Chaqueta de entrenamiento con escudo en el pecho",
    "Blazer de diseño con solapa en color contrastante",
]

DECORADOS = [
    "Un vestuario moderno con las taquillas de madera oscura",
    "Pista de baloncesto interior de lujo con iluminación de neón dorado",
    "Un tejado urbano con vistas al puente Golden Gate al atardecer",
    "Un túnel de estadio de hormigón con luces rojas intensas",
    "Una calle de Manhattan de noche con rascacielos iluminados",
    "Un ático de lujo con piscina y vistas a la playa al amanecer",
    "Un entorno industrial limpio y minimalista con acero visto",
    "Un pasillo estrecho con paredes de metal corrugado y luces rojas",
    "Una sala de estar moderna con decoración futurista y pantallas",
    "Una biblioteca moderna con estanterías de metal y cristal",
    "Un garaje de carreras con herramientas colgadas y neones amarillos",
    "Un muelle al atardecer sobre el océano Pacífico",
    "Un bosque neblinoso al amanecer con una cancha de madera rústica",
    "Una cabaña de lujo moderna con chimenea encendida y nieve exterior",
    "Un paisaje helado con una aurora boreal en el cielo",
    "Una calle del Barrio Francés de Nueva Orleans con balcones de hierro",
    "Una estación de metro de Nueva York con azulejos blancos históricos",
    "Una llanura abierta bajo un cielo de tormenta eléctrica dramático",
    "Un parque temático mágico con fuegos artificiales de fondo",
    "Un salón histórico con la campana de la libertad y techos altos",
    "Un pabellón futurista con luces LED multicolor",
    "Un parqué clásico con el trébol gigante pintado en el suelo",
    "Una cancha callejera en Brooklyn bajo un puente de acero",
    "Un túnel de vestuarios con luces rojas y humo dramático",
    "Una antigua fundición de acero reformada como cancha de baloncesto",
    "Un skyline nocturno de una ciudad moderna iluminada de fondo",
    "La cima de una montaña nevada con una canasta de madera rústica",
    "Un patio histórico de piedra con arquitectura clásica española",
    "Un garaje moderno con iluminación de neón azul y roja",
    "Un paseo marítimo urbano del Mediterráneo con vistas al puerto",
    "Una estación de metro futurista con iluminación verde intensa",
    "Un bar de cócteles sofisticado con iluminación dramática",
    "Una oficina tecnológica moderna con vistas a la ciudad",
    "Un muro de graffiti en una calle urbana vibrante",
    "Un callejón de hormigón brutalista",
    "Una galería de arte moderna con esculturas minimalistas",
    "Un parque arbolado moderno con arquitectura de madera",
    "Una plaza monumental con arquitectura imperial",
    "Una plaza central europea con suelos de adoquines históricos",
    "Un pabellón italiano antiguo con techo abovedado",
    "Una cancha costera con el mar Adriático de fondo al atardecer",
    "Un pabellón moderno con arquitectura vanguardista",
    "Un estadio olímpico imponente con columnas griegas modernas",
    "Una plaza histórica italiana con pórticos de ladrillo medievales",
    "Un pabellón cubierto de nieve con luces interiores cálidas",
    "Una caldera de pabellón con ambiente denso, oscuro y humo",
    "Una cancha urbana en un parque europeo tradicional con árboles",
    "Un set de rodaje cinematográfico de Hollywood con focos potentes",
    "Una playa al atardecer con luces de neón rosa y azul en los bares",
    "El puerto de Mónaco al atardecer con yates de lujo",
    "Una pasarela de moda de Milán con flashes de fotógrafos",
    "El Allianz Arena iluminado de noche en el color del equipo",
    "El Burj Khalifa iluminado de noche con el desierto de fondo",
    "Los muelles del Sena de noche con la Torre Eiffel iluminada",
    "Un paisaje desértico con cactus gigantes y un sol naranja intenso",
    "Un bosque de secuoyas al amanecer con niebla baja",
    "Una sala del trono modernizada con iluminación dramática",
    "Un local de jazz con luces cálidas y humo de ambiente",
    "El Capitolio de Washington iluminado de noche",
    "Una fábrica de automóviles reconvertida en pabellón de baloncesto",
    "Una discoteca urbana con luces de neón de colores del equipo",
]

TIPOS_LOGO = [
    "Parche grande bordado en el pecho",
    "Serigrafía de graffiti en la espalda",
    "Texto sutil bordado en el lateral de la capucha",
    "Logotipo de graffiti grande impreso en el pantalón",
    "Pin metálico estilizado en la solapa de la chaqueta",
    "Parche sutil de estilo neón en el lateral",
    "Texto de graffiti grande y audaz en el pecho",
    "Texto de graffiti vertical a lo largo de la cremallera",
    "Bordado de marca de lujo en la manga",
    "Parche bordado en el dobladillo inferior",
    "Graffiti con efecto de velocidad en la puerta del garaje",
    "Graffiti estilo Old English en un poste de madera",
    "Graffiti con marcas de garras en un tronco caído",
    "Graffiti elegante sobre una pared de piedra volcánica",
    "Graffiti que brilla en la oscuridad sobre el hielo",
    "Graffiti artístico y colorido en una pared de ladrillo visto",
    "Graffiti clásico de los años 80 sobre los azulejos de la estación",
    "Graffiti eléctrico con rayos sobre una valla metálica",
    "Graffiti con purpurina y brillo sobre un muro negro",
    "Graffiti con estilo de caligrafía colonial en una columna",
    "Texto de graffiti en los marcadores digitales del pabellón",
    "Graffiti integrado en las vetas de la madera del suelo",
    "Tipografía de estilo metro neoyorquino en la pared de hormigón",
    "Graffiti agresivo y de gran tamaño en la puerta del túnel",
    "Graffiti con efecto metálico sobre una viga de acero",
    "Logo brillante en un cartel publicitario de neón",
    "Graffiti tallado en la roca de la montaña con efecto natural",
    "Graffiti estilizado sobre el cristal del ventanal con spray dorado",
    "Estilo Hollywood en graffiti dorado sobre el fondo de estudio",
    "Graffiti de neón vibrante sobre la arena húmeda",
    "Logotipo de graffiti sutil y elegante en la solapa",
    "Estampado grande y audaz de estilo urbano en la espalda",
    "Parche de graffiti en la manga de la chaqueta",
    "Texto de graffiti con símbolo del equipo en la pierna del chándal",
    "Bordado de marca sutil en el cuello de la camisa",
    "Logotipo de graffiti sutil bordado en el pecho",
    "Texto de graffiti grande y audaz integrado en el muro de fondo",
    "Texto de graffiti crudo y grande impreso en el pecho",
    "Logotipo de graffiti sutil y elegante en el bolsillo interior",
    "Parche de graffiti grande en la espalda de la parka",
    "Graffiti de estilo constructivista en un muro de piedra",
    "Graffiti con textura de desgaste salino en un contenedor de carga",
    "Graffiti de estilo old school en la pared de ladrillo",
    "Graffiti minimalista sobre una fuente de piedra",
    "Graffiti de estilo retro en una pared de piedra caliza",
    "Graffiti artístico en los cristales de un palco VIP",
    "Graffiti de estilo clásico sobre una superficie de mármol blanco",
    "Graffiti minimalista y elegante en una columna de ladrillo",
    "Graffiti con efecto de escarcha sobre una valla de madera",
    "Graffiti rebelde y rudo sobre el hormigón del túnel de vestuarios",
    "Graffiti colorido sobre un banco de madera del parque",
    "Monograma de graffiti elegante en el forro interior",
    "Graffiti de estilo bávaro con escudo en la pared de ladrillo",
    "Graffiti con silueta del símbolo del equipo en fachada moderna",
    "Graffiti de estilo parisino sobre un muro de piedra del boulevard",
    "Graffiti de estrella gigante sobre el hormigón del estadio",
]


# ──────────────────────────────────────────────────────────────────────────────
# Inserción
# ──────────────────────────────────────────────────────────────────────────────

def populate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Crear tablas
    for stmt in DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            c.execute(stmt)
    print("Tablas verificadas/creadas.")

    # teams_metadata
    sql_team = """
        INSERT OR IGNORE INTO teams_metadata
            (code, name, liga, color_primary, color_secondary, color_accent, color_extra)
        VALUES (?,?,?,?,?,?,?)
    """
    nba_rows = [(c2, n, "NBA", cp, cs, ca, ce) for c2, n, cp, cs, ca, ce in NBA]
    euro_rows = [(c2, n, "EUROLIGA", cp, cs, ca, ce) for c2, n, cp, cs, ca, ce in EURO]

    c.executemany(sql_team, nba_rows)
    print(f"  NBA insertados: {c.rowcount}/{len(nba_rows)}")
    c.executemany(sql_team, euro_rows)
    print(f"  EuroLeague insertados: {c.rowcount}/{len(euro_rows)}")

    # Dimensiones
    for tabla, datos in [
        ("dim_posturas",    POSTURAS),
        ("dim_vestimentas", VESTIMENTAS),
        ("dim_decorados",   DECORADOS),
        ("dim_tipos_logo",  TIPOS_LOGO),
    ]:
        c.executemany(
            f"INSERT OR IGNORE INTO {tabla} (valor) VALUES (?)",
            [(v,) for v in datos]
        )
        print(f"  {tabla}: {c.rowcount}/{len(datos)} insertados")

    conn.commit()

    # Verificación
    print("\n── Verificación ──────────────────────────────────")
    for tabla in ["teams_metadata", "dim_posturas", "dim_vestimentas", "dim_decorados", "dim_tipos_logo"]:
        c.execute(f"SELECT COUNT(*) FROM {tabla}")
        print(f"  {tabla:25s}: {c.fetchone()[0]:3d} filas")

    # Demo: prompt aleatorio
    print("\n── Demo: prompt aleatorio ────────────────────────")
    c.execute("""
        SELECT
            'Avatar del equipo ' || t.name ||
            ' | Colores: ' || t.color_primary || ' / ' || t.color_secondary ||
            ' | Postura: ' || p.valor ||
            ' | Vestimenta: ' || v.valor ||
            ' | Decorado: ' || d.valor ||
            ' | Logo: ' || l.valor
        FROM teams_metadata t,
             (SELECT valor FROM dim_posturas    ORDER BY RANDOM() LIMIT 1) p,
             (SELECT valor FROM dim_vestimentas ORDER BY RANDOM() LIMIT 1) v,
             (SELECT valor FROM dim_decorados   ORDER BY RANDOM() LIMIT 1) d,
             (SELECT valor FROM dim_tipos_logo  ORDER BY RANDOM() LIMIT 1) l
        ORDER BY RANDOM() LIMIT 1
    """)
    print(" ", c.fetchone()[0])

    # Combinaciones posibles
    c.execute("SELECT COUNT(*) FROM teams_metadata")
    n_equipos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dim_posturas")
    n_pos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dim_vestimentas")
    n_vest = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dim_decorados")
    n_dec = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dim_tipos_logo")
    n_logo = c.fetchone()[0]
    total = n_equipos * n_pos * n_vest * n_dec * n_logo
    print(f"\n  Combinaciones únicas posibles: {total:,}")

    conn.close()
    print("\nPoblación completada.")


if __name__ == "__main__":
    populate()
