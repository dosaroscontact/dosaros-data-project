"""
seed_avatar_teams.py — Pobla avatar_teams con todos los equipos NBA y EuroLeague.

Datos extraídos de assets/docs/Descripción.txt
Los equipos sin variación en el documento reciben colores oficiales
y plantillas genéricas coherentes con su identidad visual.

Uso:
    python src/etl/seed_avatar_teams.py
"""

import os
import sqlite3

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# ──────────────────────────────────────────────
# Datos: NBA (30 equipos, múltiples variaciones)
# ──────────────────────────────────────────────
NBA_TEAMS = [
    # (team_code, team_name, color_a, color_b, color_c, color_d,
    #  postura, vestimenta, decorado, tipo_logo, variacion_idx)

    # ── Atlanta Hawks ──
    ("ATL", "Atlanta Hawks",
     "Rojo", "Blanco", "Verde Volt", None,
     "saltando para un tapón espectacular",
     "equipación oficial con detalles en verde neón",
     "un pabellón futurista con luces LED multicolor",
     "texto de graffiti en los marcadores digitales del pabellón",
     1),

    # ── Boston Celtics ──
    ("BOS", "Boston Celtics",
     "Verde Trébol", "Blanco", "Oro", None,
     "de pie, con los brazos cruzados, actitud serena y confiada",
     "camiseta de baloncesto de juego oficial",
     "un vestuario moderno con las taquillas de madera oscura",
     "parche grande bordado en el pecho con el trébol",
     1),
    ("BOS", "Boston Celtics",
     "Verde", "Blanco", "Oro", None,
     "lanzando un tiro libre con máxima concentración",
     "camiseta clásica de tirantes con número",
     "un parqué clásico con el trébol gigante pintado en el suelo",
     "graffiti integrado en las vetas de la madera del suelo",
     2),

    # ── Brooklyn Nets ──
    ("BKN", "Brooklyn Nets",
     "Negro", "Blanco", "Gris", None,
     "de pie con actitud desafiante, mirada directa a cámara",
     "sudadera sin mangas con capucha y estampado minimalista",
     "una cancha callejera en Brooklyn bajo un puente de acero",
     "tipografía de estilo metro neoyorquino en la pared de hormigón",
     1),

    # ── Charlotte Hornets ──
    ("CHA", "Charlotte Hornets",
     "Púrpura", "Teal", "Oro", None,
     "de pie, señalando hacia arriba con el dedo índice",
     "camiseta de baloncesto con detalles en teal fluorescente",
     "una discoteca urbana con luces de neón moradas y verdes",
     "graffiti brillante con efecto neón sobre una pared negra",
     1),

    # ── Chicago Bulls ──
    ("CHI", "Chicago Bulls",
     "Rojo Toro", "Negro", "Blanco", None,
     "caminando hacia la cámara por un túnel de estadio",
     "pantalones de chándal y camiseta técnica ajustada",
     "un túnel de estadio de hormigón con luces rojas intensas",
     "logotipo de graffiti grande impreso en la pierna del pantalón",
     1),
    ("CHI", "Chicago Bulls",
     "Rojo", "Negro", "Blanco", None,
     "en el aire realizando un mate explosivo",
     "pantalones cortos anchos y zapatillas retro de los 90",
     "un túnel de vestuarios con luces rojas y humo dramático",
     "graffiti agresivo y de gran tamaño en la puerta del túnel",
     2),

    # ── Cleveland Cavaliers ──
    ("CLE", "Cleveland Cavaliers",
     "Granate", "Oro", "Azul Marino", None,
     "defendiendo con los brazos extendidos en posición baja",
     "camiseta de entrenamiento técnica con detalles en oro",
     "una antigua fundición de acero reformada como cancha de baloncesto",
     "graffiti con efecto metálico sobre una viga de acero",
     1),

    # ── Dallas Mavericks ──
    ("DAL", "Dallas Mavericks",
     "Azul Mavericks", "Azul Marino", "Plata", None,
     "sentado en un sofá de cuero moderno con un balón en la mano",
     "polo deportivo de alta calidad con bordado en el pecho",
     "una sala de estar moderna con decoración futurista y pantallas",
     "bordado de marca de lujo en la manga del polo",
     1),
    ("DAL", "Dallas Mavericks",
     "Azul Real", "Plata", "Negro", None,
     "realizando un pase de pecho con fuerza y precisión",
     "camiseta de manga corta de compresión de alto rendimiento",
     "un skyline nocturno de una ciudad moderna iluminada de fondo",
     "logo brillante en un cartel publicitario de neón",
     2),

    # ── Denver Nuggets ──
    ("DEN", "Denver Nuggets",
     "Azul Medianoche", "Amarillo Sol", "Rojo Plano", None,
     "señalando al cielo con el índice tras anotar un triple",
     "camiseta con el diseño del arcoíris retro de los 70",
     "la cima de una montaña nevada con una canasta de madera rústica",
     "graffiti tallado en la roca de la montaña con efecto natural",
     1),

    # ── Detroit Pistons ──
    ("DET", "Detroit Pistons",
     "Azul", "Rojo", "Blanco", None,
     "de pie en una pose industrial, brazos cruzados sobre el pecho",
     "chaqueta de trabajo técnica con detalles metálicos",
     "una fábrica de automóviles reconvertida en pabellón de baloncesto",
     "graffiti industrial con tuercas y pistones en la pared de metal",
     1),

    # ── Golden State Warriors ──
    ("GSW", "Golden State Warriors",
     "Azul Real", "Amarillo California", "Blanco", None,
     "de pie mirando hacia un lado, con un pie apoyado en una caja",
     "sudadera con capucha estilizada de corte moderno",
     "un tejado urbano con vistas al puente Golden Gate al atardecer",
     "texto sutil bordado en el lateral de la capucha",
     1),
    ("GSW", "Golden State Warriors",
     "Azul", "Amarillo", "Blanco", None,
     "celebrando con los brazos abiertos en posición triunfal",
     "chaqueta de calentamiento moderna con cremallera completa",
     "el puente Golden Gate visible a través de grandes ventanales panorámicos",
     "graffiti estilizado sobre el cristal del ventanal con spray dorado",
     2),

    # ── Houston Rockets ──
    ("HOU", "Houston Rockets",
     "Rojo", "Plata", "Blanco", None,
     "preparado para el despegue, rodilla elevada en pose dinámica",
     "camiseta de baloncesto con detalles plateados metálicos",
     "una plataforma de lanzamiento espacial con cohete de fondo",
     "graffiti estilo NASA con letras técnicas en una estructura metálica",
     1),

    # ── Indiana Pacers ──
    ("IND", "Indiana Pacers",
     "Azul Marino", "Oro", "Plata", None,
     "en posición de defensa baja deslizándose lateralmente",
     "camiseta con líneas verticales finas estilo pinstripes",
     "un garaje de carreras con herramientas colgadas y neones amarillos",
     "graffiti con efecto de velocidad en la puerta metálica del garaje",
     1),

    # ── LA Clippers ──
    ("LAC", "LA Clippers",
     "Azul", "Rojo", "Blanco", None,
     "saltando para un rebote con los dos brazos completamente extendidos",
     "equipación moderna con tipografía náutica y detalles marineros",
     "un muelle al atardecer sobre el océano Pacífico con gaviotas",
     "graffiti estilo Old English en un poste de madera del muelle",
     1),

    # ── Los Angeles Lakers ──
    ("LAL", "Los Angeles Lakers",
     "Púrpura", "Oro", "Blanco", None,
     "sentado en el suelo de una pista interior, sujetando un balón con una mano",
     "chaqueta de chándal retro con franjas doradas en los laterales",
     "pista de baloncesto interior de lujo con iluminación de neón dorado",
     "serigrafía de graffiti dorada en la espalda de la chaqueta",
     1),
    ("LAL", "Los Angeles Lakers",
     "Púrpura", "Oro", "Blanco", None,
     "caminando por una alfombra roja con un balón bajo el brazo",
     "camiseta de tirantes con detalles dorados y lentejuelas",
     "un set de rodaje cinematográfico de Hollywood con focos potentes",
     "estilo Hollywood en graffiti dorado sobre el fondo de estudio",
     2),

    # ── Memphis Grizzlies ──
    ("MEM", "Memphis Grizzlies",
     "Azul Grizzly", "Azul Cielo", "Oro", None,
     "rugiendo tras un tapón espectacular con los puños cerrados",
     "sudadera oversize con el logo del oso en el pecho",
     "un bosque neblinoso al amanecer con una cancha de madera rústica",
     "graffiti con marcas de garras de oso en un tronco caído",
     1),

    # ── Miami Heat ──
    ("MIA", "Miami Heat",
     "Rojo Fuego", "Negro", "Blanco", "Rosa Vice",
     "de pie de espaldas a cámara, mirando por una ventana grande",
     "camiseta de baloncesto edición Vice con degradados de color",
     "un ático de lujo con piscina y vistas a la playa al amanecer",
     "parche sutil de estilo neón en el lateral de la camiseta",
     1),
    ("MIA", "Miami Heat",
     "Rojo", "Negro", "Blanco", None,
     "apoyado en una palmera con un balón de fuego en la mano",
     "camiseta City Edition con degradados rosa y cian",
     "una playa al atardecer con luces de neón rosa y azul en los bares",
     "graffiti de neón vibrante sobre la arena húmeda",
     2),

    # ── Milwaukee Bucks ──
    ("MIL", "Milwaukee Bucks",
     "Verde Bosque", "Crema", "Azul", None,
     "flexionando los músculos con expresión intensa tras un mate",
     "camiseta con detalles en color crema edición City Edition",
     "una cabaña de lujo moderna con chimenea encendida y nieve exterior",
     "graffiti elegante con astas de ciervo sobre una pared de piedra volcánica",
     1),

    # ── Minnesota Timberwolves ──
    ("MIN", "Minnesota Timberwolves",
     "Azul Medianoche", "Verde Aurora", "Gris", None,
     "mirando fijamente a cámara con intensidad gélida",
     "chaqueta técnica reflectante de entrenamiento nocturno",
     "un paisaje helado de Minnesota con una aurora boreal en el cielo",
     "graffiti que brilla en la oscuridad sobre el hielo agrietado",
     1),

    # ── New Orleans Pelicans ──
    ("NOP", "New Orleans Pelicans",
     "Azul Marino", "Oro", "Rojo", None,
     "haciendo el gesto de silencio con el dedo índice en los labios",
     "camiseta con detalles de carnaval y lentejuelas doradas",
     "una calle del Barrio Francés de Nueva Orleans con balcones de hierro",
     "graffiti artístico y colorido en una pared de ladrillo visto",
     1),

    # ── New York Knicks ──
    ("NYK", "New York Knicks",
     "Azul Knicks", "Naranja Knicks", "Plata", None,
     "de pie con las manos en los bolsillos de la chaqueta, actitud cool",
     "chaqueta bomber elegante y moderna con parches",
     "una calle de Manhattan de noche con rascacielos iluminados",
     "pin metálico estilizado en la solapa de la chaqueta bomber",
     1),
    ("NYK", "New York Knicks",
     "Naranja", "Azul", "Blanco", None,
     "botando el balón entre las piernas con velocidad y control",
     "camiseta clásica con el cuello redondo y número en el pecho",
     "una estación de metro de Nueva York con azulejos blancos históricos",
     "graffiti clásico de los años 80 sobre los azulejos de la estación",
     2),

    # ── Oklahoma City Thunder ──
    ("OKC", "Oklahoma City Thunder",
     "Azul Celeste", "Naranja", "Amarillo", None,
     "preparado para salir en contraataque con expresión eléctrica",
     "equipación con rayos eléctricos en los laterales",
     "una llanura abierta bajo un cielo de tormenta eléctrica dramático",
     "graffiti eléctrico con rayos sobre una valla metálica oxidada",
     1),

    # ── Orlando Magic ──
    ("ORL", "Orlando Magic",
     "Azul", "Negro", "Plata", None,
     "lanzando un triple desde la esquina con forma perfecta",
     "camiseta con estrellas metálicas impresas en los laterales",
     "un parque temático mágico con fuegos artificiales de fondo",
     "graffiti con purpurina y brillo de colores sobre un muro negro",
     1),

    # ── Philadelphia 76ers ──
    ("PHI", "Philadelphia 76ers",
     "Azul Real", "Rojo", "Blanco", "Oro",
     "de pie con un pie sobre una silla, mirando a cámara con confianza",
     "camiseta de baloncesto de manga corta estilizada con detalles",
     "una biblioteca moderna con estanterías de metal y cristal",
     "parche bordado en el dobladillo inferior de la camiseta",
     1),
    ("PHI", "Philadelphia 76ers",
     "Azul", "Rojo", "Blanco", None,
     "cruzando los brazos en señal de confianza y determinación",
     "camiseta de estilo histórico con estrellas bordadas",
     "un salón histórico con la campana de la libertad y techos altos",
     "graffiti con estilo de caligrafía colonial en una columna de mármol",
     2),

    # ── Phoenix Suns ──
    ("PHX", "Phoenix Suns",
     "Púrpura", "Naranja", "Oro", None,
     "de pie bajo el sol del desierto, visera en la mano",
     "camiseta con degradado del atardecer del desierto de Arizona",
     "un paisaje desértico con cactus gigantes y un sol naranja intenso",
     "graffiti con colores del atardecer sobre una roca de arenisca",
     1),

    # ── Portland Trail Blazers ──
    ("POR", "Portland Trail Blazers",
     "Rojo", "Negro", "Blanco", None,
     "abriendo camino entre la espesura con determinación",
     "cortavientos técnico rojo con el logo en el pecho",
     "un bosque de secuoyas al amanecer con niebla baja",
     "graffiti de estilo forestal tallado en la corteza de un árbol gigante",
     1),

    # ── Sacramento Kings ──
    ("SAC", "Sacramento Kings",
     "Púrpura", "Plata", "Negro", None,
     "de pie en postura real, con la corona implícita en la actitud",
     "chaqueta de terciopelo morado con detalles plateados",
     "una sala del trono modernizada con iluminación morada dramática",
     "graffiti de estilo real con corona sobre una columna dorada",
     1),

    # ── San Antonio Spurs ──
    ("SAS", "San Antonio Spurs",
     "Plata Metálico", "Negro", "Blanco", None,
     "sentado en un banco metálico, en actitud pensativa y seria",
     "sudadera sin mangas con capucha en gris metálico",
     "un entorno industrial limpio y minimalista con acero visto",
     "texto de graffiti grande y audaz en el pecho de la sudadera",
     1),

    # ── Toronto Raptors ──
    ("TOR", "Toronto Raptors",
     "Rojo Raptors", "Negro", "Plata", None,
     "de pie en una pose de hype total, con los brazos abiertos",
     "cortavientos técnico de estilo urbano con cremallera lateral",
     "un pasillo estrecho con paredes de metal corrugado y luces rojas",
     "texto de graffiti vertical a lo largo de la cremallera del cortavientos",
     1),

    # ── Utah Jazz ──
    ("UTA", "Utah Jazz",
     "Azul Marino", "Oro", "Blanco", None,
     "de pie tocando una trompeta imaginaria con elegancia y ritmo",
     "camiseta de baloncesto con detalles de notas musicales",
     "un local de jazz de Salt Lake City con luces cálidas y humo",
     "graffiti de notas musicales y ondas de sonido en la pared del local",
     1),

    # ── Washington Wizards ──
    ("WAS", "Washington Wizards",
     "Azul Marino", "Rojo", "Blanco", None,
     "de pie en postura de mago, con un balón flotando ante él",
     "camiseta con estrellas y detalles de constelaciones en el tejido",
     "el Capitolio de Washington iluminado de noche con magia visual",
     "graffiti con estrellas y constelaciones sobre una columna de mármol",
     1),
]

# ──────────────────────────────────────────────
# Datos: EuroLeague (activos + históricos)
# ──────────────────────────────────────────────
EURO_TEAMS = [
    # ── Real Madrid ──
    ("MAD", "Real Madrid",
     "Blanco", "Púrpura Real", "Oro", None,
     "de pie en una pose majestuosa y elegante, ligeramente elevado",
     "chaqueta de traje de lino de diseño italiano",
     "un patio histórico de piedra con arquitectura clásica española",
     "logotipo de graffiti sutil y elegante en la solapa de la chaqueta",
     1),

    # ── FC Barcelona ──
    ("BAR", "FC Barcelona",
     "Azul", "Grana", "Amarillo", None,
     "de pie, apoyado en un coche deportivo moderno con actitud",
     "camiseta técnica de running de alta gama con rayas azulgranas",
     "un garaje moderno con iluminación de neón azul y roja",
     "estampado grande y audaz de estilo urbano en la espalda",
     1),
    ("BAR", "FC Barcelona",
     "Azul", "Grana", "Amarillo", None,
     "entrando a canasta con una bandeja fluida y elegante",
     "equipación azulgrana clásica con detalles en amarillo",
     "un pabellón moderno con arquitectura vanguardista catalana",
     "graffiti artístico en los cristales de un palco VIP",
     2),

    # ── Olympiacos ──
    ("OLY", "Olympiacos BC",
     "Rojo", "Blanco", "Negro", None,
     "sentado en una moto tipo scooter moderna con actitud",
     "chaqueta de cuero estilo biker con tachuelas en los hombros",
     "un paseo marítimo urbano del Pireo con vistas al puerto",
     "parche de graffiti en la manga de la chaqueta de cuero",
     1),
    ("OLY", "Olympiacos BC",
     "Rojo", "Blanco", "Plata", None,
     "remando simbólicamente con un balón en las manos",
     "camiseta de rayas verticales rojas y blancas clásica",
     "un puerto marítimo del Mediterráneo con barcos clásicos al fondo",
     "graffiti con textura de desgaste salino en un contenedor de carga",
     2),

    # ── Panathinaikos ──
    ("PAN", "Panathinaikos AKTOR",
     "Verde", "Blanco", "Oro", None,
     "de pie en una pose dinámica con un salto sutil del suelo",
     "conjunto de chándal completo moderno en verde y blanco",
     "una estación de metro futurista de Atenas con iluminación verde",
     "texto de graffiti con trébol integrado en la pierna del chándal",
     1),
    ("PAN", "Panathinaikos AKTOR",
     "Verde", "Blanco", "Oro", None,
     "levantando el puño en señal de victoria con mirada intensa",
     "camiseta con el trébol bordado en el lateral",
     "un estadio olímpico imponente con columnas griegas modernas",
     "graffiti de estilo clásico sobre una superficie de mármol blanco",
     2),

    # ── Fenerbahçe ──
    ("ULK", "Fenerbahçe Beko",
     "Azul Marino", "Amarillo", "Blanco", None,
     "de pie con una pose de modelo, mirando a cámara con confianza",
     "camisa de seda estampada de lujo con ribetes amarillos",
     "un bar de cócteles sofisticado de Estambul con iluminación dramática",
     "bordado de marca sutil y elegante en el cuello de la camisa",
     1),

    # ── Anadolu Efes ──
    ("IST", "Anadolu Efes",
     "Azul Efes", "Blanco", "Rojo", None,
     "sentado en un sillón de diseño futurista con una tablet",
     "suéter de punto de alta calidad azul con cuello vuelto",
     "una oficina tecnológica moderna de Estambul con vistas al Bósforo",
     "logotipo de graffiti sutil bordado en el pecho del suéter",
     1),

    # ── Maccabi Tel Aviv ──
    ("TEL", "Maccabi Playtika Tel Aviv",
     "Amarillo", "Azul", "Oro", None,
     "de pie en pose de acción, simulando un lanzamiento explosivo",
     "pantalones cortos de baloncesto y camiseta interior técnica amarilla",
     "un muro de graffiti en una calle urbana vibrante de Tel Aviv",
     "texto de graffiti grande y audaz integrado en el muro de fondo",
     1),
    ("TEL", "Maccabi Playtika Tel Aviv",
     "Amarillo", "Azul", "Blanco", None,
     "sosteniendo un trofeo con ambas manos sobre la cabeza",
     "equipación clásica de color amarillo brillante con la estrella de David",
     "un pabellón lleno de banderas amarillas y confeti dorado",
     "graffiti en bloque sobre una lona gigante de celebración",
     2),

    # ── Partizan Belgrade ──
    ("PAR", "Partizan Mozzart Bet",
     "Negro", "Blanco", "Plata", None,
     "de pie con una pose seria y minimalista, inmóvil como una estatua",
     "sudadera con capucha de algodón pesado heavyweight negra",
     "un callejón de hormigón brutalista de Belgrado con graffiti de fondo",
     "texto de graffiti grande y crudo impreso en el pecho de la sudadera",
     1),
    ("PAR", "Partizan Mozzart Bet",
     "Negro", "Blanco", "Gris", None,
     "gritando de emoción tras un triple decisivo en el último segundo",
     "camiseta negra sobria con detalles geométricos en blanco",
     "una caldera de pabellón con ambiente denso, oscuro y humo",
     "graffiti rebelde y rudo sobre el hormigón del túnel de vestuarios",
     2),

    # ── Virtus Bologna ──
    ("VIR", "Virtus Segafredo Bologna",
     "Blanco", "Negro", "Oro", None,
     "sentado en una silla de diseño clásico italiano con elegancia",
     "chaqueta blazer desestructurada en blanco con solapa negra",
     "una galería de arte moderna de Bolonia con esculturas minimalistas",
     "logotipo de graffiti sutil y elegante en el bolsillo interior",
     1),
    ("VIR", "Virtus Segafredo Bologna",
     "Negro", "Blanco", "Plata", None,
     "defendiendo intensamente con las manos bajas en posición de alerta",
     "camiseta negra con la V blanca característica de Virtus",
     "una plaza histórica italiana con pórticos de ladrillo medievales",
     "graffiti minimalista y elegante en una columna de ladrillo antiguo",
     2),

    # ── Zalgiris Kaunas ──
    ("ZAL", "Zalgiris Kaunas",
     "Verde", "Blanco", "Negro", None,
     "de pie en una pose relajada con los brazos cruzados naturalmente",
     "parka técnica de estilo urbano verde con forro interior visible",
     "un parque arbolado moderno de Kaunas con arquitectura de madera",
     "parche de graffiti grande en la espalda de la parka",
     1),
    ("ZAL", "Zalgiris Kaunas",
     "Verde", "Blanco", "Verde Oscuro", None,
     "atrapando un rebote con fuerza y determinación en el aire",
     "camiseta técnica con patrones inspirados en el bosque lituano",
     "un pabellón cubierto de nieve con luces interiores cálidas y acogedoras",
     "graffiti con efecto de escarcha sobre una valla de madera natural",
     2),

    # ── AS Monaco ──
    ("MCO", "AS Monaco",
     "Rojo", "Blanco", "Negro", None,
     "de pie en la terraza de un yate con actitud elegante",
     "traje de sport rojo con pantalón blanco de lino",
     "el puerto de Mónaco al atardecer con yates de lujo",
     "logotipo de graffiti sofisticado en el bolsillo del traje",
     1),

    # ── EA7 Emporio Armani Milano ──
    ("MIL", "EA7 Emporio Armani Milano",
     "Blanco", "Rojo", "Negro", None,
     "de pie en pose de alta moda, mirada al frente con estilo",
     "blazer de diseño italiano blanco con detalles en rojo",
     "una pasarela de moda de Milán con flashes de fotógrafos",
     "monograma de graffiti elegante en el forro interior del blazer",
     1),

    # ── Bayern Munich ──
    ("MUN", "FC Bayern Munich",
     "Rojo", "Blanco", "Azul Bavaria", None,
     "de pie con los brazos en jarra, pose de campeón absoluto",
     "chaqueta de entrenamiento roja con escudo en el pecho",
     "el Allianz Arena iluminado en rojo por la noche",
     "graffiti de estilo bávaro con el escudo en una pared de ladrillo",
     1),

    # ── LDLC ASVEL ──
    ("ASV", "LDLC ASVEL",
     "Azul", "Amarillo", "Blanco", None,
     "de pie con postura dinámica mirando al horizonte con determinación",
     "camiseta de baloncesto azul con detalles en amarillo fluorescente",
     "las calles modernas de Lyon con el río Ródano de fondo",
     "graffiti moderno y urbano sobre una pared de ladrillo visto",
     1),

    # ── Baskonia ──
    ("BAS", "TD Systems Baskonia",
     "Azul", "Rojo", "Blanco", None,
     "de pie en postura vasca tradicional adaptada, con orgullo",
     "camiseta técnica con detalles geométricos vascos en los bordes",
     "un caserío vasco moderno con montañas verdes al fondo",
     "graffiti de diseño geométrico vasco en una pared de piedra",
     1),

    # ── Dubai Basketball ──
    ("DUB", "Dubai Basketball",
     "Negro", "Oro", "Blanco", None,
     "de pie ante el skyline de Dubai con actitud de magnate",
     "traje negro de lujo con detalles en hilo dorado",
     "el Burj Khalifa iluminado de noche con el desierto de fondo",
     "logotipo de graffiti dorado sobre una placa de mármol negro",
     1),

    # ── Hapoel Tel Aviv ──
    ("HTA", "Hapoel Tel Aviv",
     "Rojo", "Negro", "Blanco", None,
     "de pie en postura de trabajador orgulloso, puño al frente",
     "camiseta de baloncesto roja con estrella roja en el pecho",
     "el puerto antiguo de Jaffa con las luces de Tel Aviv de fondo",
     "graffiti de estilo obrero con estrella roja en una pared de hormigón",
     1),

    # ── Valencia Basket ──
    ("PAM", "Valencia Basket",
     "Negro", "Naranja", "Blanco", None,
     "de pie con los brazos extendidos en la pose del murciélago",
     "camiseta negra con el murciélago naranja estampado en el pecho",
     "la ciudad de Valencia con la Ciudad de las Artes y las Ciencias",
     "graffiti con silueta de murciélago gigante sobre una fachada moderna",
     1),

    # ── Paris Basketball ──
    ("PRS", "Paris Basketball",
     "Azul", "Rojo", "Blanco", None,
     "de pie ante la Torre Eiffel con actitud artística y cool",
     "bomber francesa con detalles en azul, blanco y rojo tricolor",
     "los muelles del Sena de noche con la Torre Eiffel iluminada",
     "graffiti de estilo parisino sobre un muro de piedra del boulevard",
     1),

    # ── Crvena Zvezda (Estrella Roja) ──
    ("RED", "Crvena Zvezda mts",
     "Rojo", "Blanco", "Azul", None,
     "de pie con los brazos en cruz formando la estrella, pose épica",
     "camiseta con la estrella de cinco puntas rojas en el pecho",
     "el estadio Marakana de Belgrado con la afición en rojo y blanco",
     "graffiti de estrella roja gigante sobre hormigón del estadio",
     1),

    # ── Equipos históricos ──
    ("CSK", "CSKA Moscow",
     "Rojo", "Azul", "Oro", None,
     "firme, con una mirada gélida y profesional en posición de guardia",
     "chándal de entrenamiento de alta gama rojo con detalles dorados",
     "una plaza monumental de Moscú con arquitectura imperial soviética",
     "graffiti de estilo constructivista ruso en un muro de piedra",
     1),

    ("CIB", "Cibona Zagreb",
     "Azul", "Blanco", "Plata", None,
     "en posición de triple amenaza, concentrado y listo para atacar",
     "camiseta técnica con detalles geométricos azules y blancos",
     "una plaza central de Zagreb con adoquines históricos europeos",
     "graffiti minimalista y moderno sobre una fuente de piedra",
     1),

    ("LIM", "Limoges CSP",
     "Amarillo", "Verde", "Blanco", None,
     "lanzando un tiro de media distancia con forma técnica perfecta",
     "equipación clásica de los años 90 en amarillo y verde",
     "una cancha urbana en un parque europeo tradicional con árboles",
     "graffiti colorido de los 90s sobre un banco de madera del parque",
     1),

    ("JUG", "Jugoplastika Split",
     "Amarillo", "Negro", "Blanco", None,
     "botando el balón con elegancia y control, mirada perdida en el horizonte",
     "equipación retro de los años 80 con el nombre 'Jugoplastika' en el pecho",
     "una cancha costera en Split con el mar Adriático de fondo al atardecer",
     "graffiti de estilo retro yugoslavo en una pared de piedra caliza",
     1),
]


# ──────────────────────────────────────────────
# Inserción
# ──────────────────────────────────────────────

def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sql = """
        INSERT OR IGNORE INTO avatar_teams
            (team_code, liga, team_name,
             color_a, color_b, color_c, color_d,
             postura, vestimenta, decorado, tipo_logo, variacion_idx)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """

    nba_rows = [
        (code, "NBA", name, ca, cb, cc, cd, pos, vest, deco, logo, var)
        for (code, name, ca, cb, cc, cd, pos, vest, deco, logo, var) in NBA_TEAMS
    ]
    euro_rows = [
        (code, "EUROLIGA", name, ca, cb, cc, cd, pos, vest, deco, logo, var)
        for (code, name, ca, cb, cc, cd, pos, vest, deco, logo, var) in EURO_TEAMS
    ]

    c.executemany(sql, nba_rows)
    print(f"NBA:      {c.rowcount} filas insertadas ({len(nba_rows)} intentadas)")
    c.executemany(sql, euro_rows)
    print(f"EUROLIGA: {c.rowcount} filas insertadas ({len(euro_rows)} intentadas)")

    conn.commit()

    c.execute("SELECT liga, COUNT(*) FROM avatar_teams GROUP BY liga")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]} variaciones en BD")

    conn.close()
    print("Seed completado.")


if __name__ == "__main__":
    seed()
