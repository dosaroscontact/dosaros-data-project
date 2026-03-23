# Guía de Generación de Avatares — Dos Aros

## Herramienta: Google ImageFX
URL: https://labs.google/fx/tools/image-fx

## Paso a paso para cada avatar

1. Abre Google ImageFX
2. Haz clic en el icono de imagen/referencia para subir foto
3. Sube assets/avatars/nba_LAL.PNG como imagen de referencia del personaje
4. Copia el prompt correspondiente al equipo
5. Genera la imagen
6. Si la cara ha cambiado, regenera añadiendo al inicio: "IMPORTANT: Keep exact same face, bald head, short gray beard, same person"
7. Descarga la imagen generada
8. Renómbrala según el naming convention
9. Cópiala a assets/avatars/
10. Haz git add, commit y push

## PROMPT BASE (incluir siempre al inicio)

3D cartoon character, bald man with short gray beard, dark sunglasses, same face and body proportions as reference image. Do NOT change facial features, head shape or body type. Green screen background #00B140. Pixar/Disney 3D style. Full body visible. Sharp clean edges for chroma key removal.

## Naming Convention
- NBA: nba_CODIGO.PNG (ejemplo: nba_GSW.PNG)
- Euroliga: euro_CODIGO.PNG (ejemplo: euro_MAD.PNG)
- Presentador: presenter_DESCRIPCION.PNG

## Estado actual de avatares

### NBA — Completados ✅
| Código | Equipo | Archivo |
|--------|--------|---------|
| LAL | Los Angeles Lakers | nba_LAL.PNG |
| BOS | Boston Celtics | nba_BOS.PNG |
| CHI | Chicago Bulls | nba_CHI.PNG |
| CHI | Chicago Bulls (gorro) | nba_CHI_gorro.PNG |
| CLE | Cleveland Cavaliers | nba_CLE.PNG |
| DEN | Denver Nuggets | nba_DEN.PNG |
| DEN | Denver Nuggets (bucket) | nba_DEN_bucket.PNG |
| DET | Detroit Pistons | nba_DET.PNG |
| MIA | Miami Heat | nba_MIA.PNG |
| SAC | Sacramento Kings | nba_SAC.PNG |
| UTA | Utah Jazz | nba_UTA.PNG |

### NBA — Pendientes ❌ (generar por orden de prioridad)
| Código | Equipo | Colores | Prompt camiseta |
|--------|--------|---------|-----------------|
| GSW | Golden State Warriors | azul/dorado | "Wearing Golden State Warriors blue and gold NBA jersey number 7, jeans, white sneakers. Pointing up with one finger. Confident champion pose." |
| OKC | Oklahoma City Thunder | azul/naranja | "Wearing OKC Thunder blue and orange NBA jersey number 7, jeans. Dynamic energetic pose, arms wide." |
| SAS | San Antonio Spurs | negro/plata | "Wearing San Antonio Spurs black and silver NBA jersey number 7, jeans. Calm composed pose, arms crossed." |
| NYK | New York Knicks | azul/naranja | "Wearing New York Knicks blue and orange NBA jersey number 7, jeans. New York street energy, cool lean pose." |
| PHX | Phoenix Suns | morado/naranja | "Wearing Phoenix Suns purple and orange NBA jersey number 7, jeans. Shooting motion, one hand raised." |
| MIL | Milwaukee Bucks | verde/crema | "Wearing Milwaukee Bucks green and cream NBA jersey number 7, jeans. Proud stance, hands on hips." |
| BKN | Brooklyn Nets | negro/blanco | "Wearing Brooklyn Nets black and white NBA jersey number 7, jeans. Cool NYC streetball pose, slight lean." |
| MIN | Minnesota Timberwolves | azul/verde | "Wearing Minnesota Timberwolves blue and green NBA jersey number 7, jeans. Surprised excited pose." |
| DAL | Dallas Mavericks | azul/plata | "Wearing Dallas Mavericks blue and silver NBA jersey number 7, jeans. Confident dribbling motion pose." |
| HOU | Houston Rockets | rojo/plata | "Wearing Houston Rockets red and silver NBA jersey number 7, jeans. Rocket launch energy, pointing up." |
| ATL | Atlanta Hawks | rojo/dorado | "Wearing Atlanta Hawks red and gold NBA jersey number 7, jeans. Passionate celebratory pose." |
| TOR | Toronto Raptors | rojo/negro | "Wearing Toronto Raptors red and black NBA jersey number 7, jeans. Fierce competitive pose." |
| POR | Portland Trail Blazers | rojo/negro | "Wearing Portland Trail Blazers red and black NBA jersey number 7, jeans. Pacific Northwest chill energy." |
| MEM | Memphis Grizzlies | azul/dorado | "Wearing Memphis Grizzlies blue and gold NBA jersey number 7, jeans. Gritty determined pose." |
| NOP | New Orleans Pelicans | azul/dorado | "Wearing New Orleans Pelicans blue and gold NBA jersey number 7, jeans. Bayou swagger pose." |
| IND | Indiana Pacers | azul/dorado | "Wearing Indiana Pacers blue and gold NBA jersey number 7, jeans. Midwest hardworking pose." |
| ORL | Orlando Magic | azul/negro | "Wearing Orlando Magic blue and black NBA jersey number 7, jeans. Magical surprised pose." |
| WAS | Washington Wizards | azul/rojo | "Wearing Washington Wizards blue and red NBA jersey number 7, jeans. Capitol city confident pose." |
| CHA | Charlotte Hornets | morado/teal | "Wearing Charlotte Hornets purple and teal NBA jersey number 7, jeans. Buzzing energy pose." |
| UTA | Utah Jazz alt | azul/dorado | "Wearing Utah Jazz navy blue and gold alternate NBA jersey number 7, jeans. Jazz musician cool pose." |

### Euroliga — Completados ✅
| Código | Equipo | Archivo |
|--------|--------|---------|
| RED | Crvena Zvezda Belgrade | euro_RED.PNG |

### Euroliga — Pendientes ❌ (generar por orden de prioridad)
| Código | Equipo | Colores | Prompt camiseta |
|--------|--------|---------|-----------------|
| MAD | Real Madrid | blanco/dorado | "Wearing Real Madrid EuroLeague white and gold jersey number 7, jeans. Royal confident pose, arms crossed." |
| BAR | FC Barcelona | azul/rojo | "Wearing FC Barcelona EuroLeague blue and red jersey number 7, jeans. Pointing upward, energetic pose." |
| OLY | Olympiacos Piraeus | rojo/blanco | "Wearing Olympiacos red and white EuroLeague jersey number 7, jeans. Passionate fist pump pose." |
| PAN | Panathinaikos | verde/negro | "Wearing Panathinaikos green and black EuroLeague jersey number 7, jeans. Thinking analytical pose." |
| ULK | Fenerbahce Istanbul | amarillo/marino | "Wearing Fenerbahce yellow and navy EuroLeague jersey number 7, jeans. Dynamic running pose." |
| IST | Anadolu Efes | azul/blanco | "Wearing Anadolu Efes light blue and white EuroLeague jersey number 7, jeans. Shooting motion pose." |
| ZAL | Zalgiris Kaunas | verde/blanco | "Wearing Zalgiris green and white EuroLeague jersey number 7, jeans. Proud hands on hips pose." |
| PAR | Partizan Belgrade | negro/blanco | "Wearing Partizan black and white EuroLeague jersey number 7, jeans. Cool relaxed pose." |
| MCO | AS Monaco | rojo/blanco | "Wearing AS Monaco red and white EuroLeague jersey number 7, jeans. Elegant one hand in pocket pose." |
| MIL | EA7 Milan | blanco/rojo | "Wearing EA7 Milan white and red EuroLeague jersey number 7, jeans. Italian stylish sideways look pose." |
| TEL | Maccabi Tel Aviv | amarillo/azul | "Wearing Maccabi Tel Aviv yellow and blue EuroLeague jersey number 7, jeans. Intense fists clenched pose." |
| HTA | Hapoel Tel Aviv | rojo/negro | "Wearing Hapoel IBI Tel Aviv red and black EuroLeague jersey number 7, jeans. Underdog victory arms raised." |
| BAS | Baskonia Vitoria | azul/rojo | "Wearing Baskonia blue and red EuroLeague jersey number 7, jeans. Defensive low stance pose." |
| PRS | Paris Basketball | azul/rojo | "Wearing Paris Basketball blue and red EuroLeague jersey number 7, jeans. Cool Parisian lean pose." |
| MUN | Bayern Munich | rojo/blanco | "Wearing Bayern Munich red and white EuroLeague jersey number 7, jeans. Power arms crossed pose." |
| VIR | Virtus Bologna | negro/blanco | "Wearing Virtus Bologna black and white EuroLeague jersey number 7, jeans. Classic pointing pose." |
| DUB | Dubai Basketball | negro/dorado | "Wearing Dubai Basketball black and gold EuroLeague jersey number 7, jeans. Luxury confident smile pose." |
| ASV | LDLC ASVEL | azul/amarillo | "Wearing LDLC ASVEL blue and yellow EuroLeague jersey number 7, jeans. Analytical hand on chin pose." |
| PAM | Valencia Basket | negro/naranja | "Wearing Valencia Basket black and orange EuroLeague jersey number 7, jeans. Energetic jumping pose." |

### Presentador — Completados ✅
| Descripción | Archivo |
|-------------|---------|
| Pizarra táctica | presenter_pizarra.jpg |
| Presentador TV | presenter_tv.jpg |
| Presentador deportes | presenter_deportes.jpg |
| Presentador Nuggets | presenter_nuggets.jpg |
| Neón v1 | presenter_neon_v1.PNG |
| Neón v2 | presenter_neon_v2.PNG |
| Playoffs | presenter_playoffs.PNG |

### Presentador — Pendientes ❌
| Descripción | Nombre archivo | Prompt |
|-------------|----------------|--------|
| Breaking news | presenter_breaking.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey with blazer. Holding papers urgently. Breaking news energy. Red blank banner at bottom." |
| Con tablet | presenter_tablet.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey. Holding iPad with blank screen. Tapping screen analytically." |
| Debate | presenter_debate.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey with blazer. Sitting on desk edge, arms open debating. Two blank screens behind." |
| Reacción viral | presenter_reaction.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey. Jaw dropped pointing off-screen left. Pure reaction meme pose." |
| Récord histórico | presenter_record.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey. Holding large blank golden trophy with both hands presenting to camera." |
| Predicción | presenter_prediction.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey. Finger pointing up, holding glowing blank crystal ball." |
| Cierre reel | presenter_closing.PNG | "[BASE PRESENTADOR] Wearing Dos Aros jersey with blazer. Thumbs up, big smile, slight bow. Sign-off pose." |

## Orden de generación recomendado

### Sesión 1 — NBA prioritarios (equipos que más aparecen en datos)
GSW → OKC → SAS → NYK → PHX → MIL

### Sesión 2 — NBA resto
BKN → MIN → DAL → HOU → ATL → TOR → POR → MEM → NOP → IND → ORL → WAS → CHA

### Sesión 3 — Euroliga prioritarios
MAD → BAR → OLY → PAN → ULK → ZAL

### Sesión 4 — Euroliga resto
IST → PAR → MCO → MIL → TEL → HTA → BAS → PRS → MUN → VIR → DUB → ASV → PAM

### Sesión 5 — Presentador
presenter_breaking → presenter_tablet → presenter_debate → presenter_reaction → presenter_record → presenter_prediction → presenter_closing

## Notas importantes

- Siempre usar nba_LAL.PNG como imagen de referencia del personaje
- Si la cara cambia regenerar añadiendo: "IMPORTANT: Keep exact same face, bald head, short gray beard, same person as reference"
- Fondo siempre #00B140 para chroma key automático
- Guardar en assets/avatars/ con naming convention exacto
- Hacer git push después de cada sesión
