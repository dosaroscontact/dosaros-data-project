# AVATAR BIBLE — Dos Aros

Referencia completa de avatares, códigos de equipo y prompts de camiseta para Google ImageFX.

## Personaje base

**3D cartoon, hombre calvo, barba corta gris, gafas de sol oscuras.**
Fondo siempre `#00B140` (green screen para chroma key automático).
Imagen de referencia del personaje: `assets/avatars/nba_LAL.PNG`

### Prompt base (incluir siempre al inicio)
```
3D cartoon character, bald man with short gray beard, dark sunglasses,
same face and body proportions as reference image.
Do NOT change facial features, head shape or body type.
Green screen background #00B140. Pixar/Disney 3D style.
Full body visible. Sharp clean edges for chroma key removal.
```

---

## NBA — 30 equipos

| Código | Equipo | Estado | Archivo | Prompt camiseta |
|--------|--------|--------|---------|-----------------|
| ATL | Atlanta Hawks | ❌ | nba_ATL.PNG | `red and gold Atlanta Hawks jersey, number 7` |
| BOS | Boston Celtics | ✅ | nba_BOS.PNG | `green and white Boston Celtics jersey, number 7` |
| BKN | Brooklyn Nets | ❌ | nba_BKN.PNG | `black and white Brooklyn Nets jersey, number 7` |
| CHA | Charlotte Hornets | ❌ | nba_CHA.PNG | `purple and teal Charlotte Hornets jersey, number 7` |
| CHI | Chicago Bulls | ✅ | nba_CHI.PNG | `red and black Chicago Bulls jersey, number 7` |
| CLE | Cleveland Cavaliers | ✅ | nba_CLE.PNG | `wine and gold Cleveland Cavaliers jersey, number 7` |
| DAL | Dallas Mavericks | ❌ | nba_DAL.PNG | `blue and silver Dallas Mavericks jersey, number 7` |
| DEN | Denver Nuggets | ✅ | nba_DEN.PNG | `navy and gold Denver Nuggets jersey, number 7` |
| DET | Detroit Pistons | ✅ | nba_DET.PNG | `blue and red Detroit Pistons jersey, number 7` |
| GSW | Golden State Warriors | ❌ | nba_GSW.PNG | `royal blue and gold Golden State Warriors jersey, number 7` |
| HOU | Houston Rockets | ❌ | nba_HOU.PNG | `red and silver Houston Rockets jersey, number 7` |
| IND | Indiana Pacers | ❌ | nba_IND.PNG | `blue and gold Indiana Pacers jersey, number 7` |
| LAC | LA Clippers | ❌ | nba_LAC.PNG | `red and blue LA Clippers jersey, number 7` |
| LAL | Los Angeles Lakers | ✅ | nba_LAL.PNG | `purple and gold Los Angeles Lakers jersey, number 7` |
| MEM | Memphis Grizzlies | ❌ | nba_MEM.PNG | `navy and gold Memphis Grizzlies jersey, number 7` |
| MIA | Miami Heat | ✅ | nba_MIA.PNG | `black and red Miami Heat jersey, number 7` |
| MIL | Milwaukee Bucks | ❌ | nba_MIL.PNG | `green and cream Milwaukee Bucks jersey, number 7` |
| MIN | Minnesota Timberwolves | ❌ | nba_MIN.PNG | `blue and green Minnesota Timberwolves jersey, number 7` |
| NOP | New Orleans Pelicans | ❌ | nba_NOP.PNG | `navy and gold New Orleans Pelicans jersey, number 7` |
| NYK | New York Knicks | ❌ | nba_NYK.PNG | `blue and orange New York Knicks jersey, number 7` |
| OKC | Oklahoma City Thunder | ❌ | nba_OKC.PNG | `blue and orange Oklahoma City Thunder jersey, number 7` |
| ORL | Orlando Magic | ❌ | nba_ORL.PNG | `blue and black Orlando Magic jersey, number 7` |
| PHI | Philadelphia 76ers | ❌ | nba_PHI.PNG | `blue and red Philadelphia 76ers jersey, number 7` |
| PHX | Phoenix Suns | ❌ | nba_PHX.PNG | `purple and orange Phoenix Suns jersey, number 7` |
| POR | Portland Trail Blazers | ❌ | nba_POR.PNG | `red and black Portland Trail Blazers jersey, number 7` |
| SAC | Sacramento Kings | ✅ | nba_SAC.PNG | `purple and silver Sacramento Kings jersey, number 7` |
| SAS | San Antonio Spurs | ❌ | nba_SAS.PNG | `black and silver San Antonio Spurs jersey, number 7` |
| TOR | Toronto Raptors | ❌ | nba_TOR.PNG | `red and black Toronto Raptors jersey, number 7` |
| UTA | Utah Jazz | ✅ | nba_UTA.PNG | `navy and gold Utah Jazz jersey, number 7` |
| WAS | Washington Wizards | ❌ | nba_WAS.PNG | `blue and red Washington Wizards jersey, number 7` |

---

## Euroliga — 20 equipos

> Nota: EA7 Milan usa código `MIL` (igual que el código de la API Euroliga). En Python se resuelve con dos dicts separados: `TEAM_JERSEY_COLORS` (NBA) y `EURO_JERSEY_COLORS` (Euroliga), donde `MIL` apunta al equipo correcto en cada liga.

| Código | Equipo | Estado | Archivo | Prompt camiseta |
|--------|--------|--------|---------|-----------------|
| ASV | LDLC ASVEL | ❌ | euro_ASV.PNG | `blue and yellow LDLC ASVEL jersey, number 7` |
| BAR | FC Barcelona | ❌ | euro_BAR.PNG | `blue and red FC Barcelona jersey, number 7` |
| BAS | Baskonia | ❌ | euro_BAS.PNG | `blue and red Baskonia jersey, number 7` |
| DUB | Dubai Basketball | ❌ | euro_DUB.PNG | `black and gold Dubai Basketball jersey, number 7` |
| HTA | Hapoel Tel Aviv | ❌ | euro_HTA.PNG | `red and black Hapoel Tel Aviv jersey, number 7` |
| IST | Anadolu Efes | ❌ | euro_IST.PNG | `blue and white Anadolu Efes jersey, number 7` |
| MAD | Real Madrid | ❌ | euro_MAD.PNG | `white and gold Real Madrid jersey, number 7` |
| MCO | AS Monaco | ❌ | euro_MCO.PNG | `red and white AS Monaco jersey, number 7` |
| MIL | EA7 Milan | ❌ | euro_MIL.PNG | `white and red EA7 Milan jersey, number 7` |
| MUN | Bayern Munich | ❌ | euro_MUN.PNG | `red and white Bayern Munich jersey, number 7` |
| OLY | Olympiacos | ❌ | euro_OLY.PNG | `red and white Olympiacos jersey, number 7` |
| PAM | Valencia Basket | ❌ | euro_PAM.PNG | `black and orange Valencia Basket jersey, number 7` |
| PAN | Panathinaikos | ❌ | euro_PAN.PNG | `green and black Panathinaikos jersey, number 7` |
| PAR | Partizan Belgrade | ❌ | euro_PAR.PNG | `black and white Partizan Belgrade jersey, number 7` |
| PRS | Paris Basketball | ❌ | euro_PRS.PNG | `blue and red Paris Basketball jersey, number 7` |
| RED | Crvena Zvezda | ✅ | euro_RED.PNG | `red and white Crvena Zvezda Belgrade jersey, number 7` |
| TEL | Maccabi Tel Aviv | ❌ | euro_TEL.PNG | `yellow and blue Maccabi Tel Aviv jersey, number 7` |
| ULK | Fenerbahce Beko | ❌ | euro_ULK.PNG | `yellow and navy Fenerbahce Beko jersey, number 7` |
| VIR | Virtus Bologna | ❌ | euro_VIR.PNG | `black and white Virtus Bologna jersey, number 7` |
| ZAL | Zalgiris Kaunas | ❌ | euro_ZAL.PNG | `green and white Zalgiris Kaunas jersey, number 7` |

---

## Presentador — avatares neutrales

| Código | Descripción | Estado | Archivo |
|--------|-------------|--------|---------|
| — | Pizarra táctica | ✅ | presenter_pizarra.jpg |
| — | Presentador TV | ✅ | presenter_tv.jpg |
| — | Presentador deportes | ✅ | presenter_deportes.jpg |
| — | Presenter Nuggets | ✅ | presenter_nuggets.jpg |
| — | Neón v1 | ✅ | presenter_neon_v1.PNG |
| — | Neón v2 | ✅ | presenter_neon_v2.PNG |
| — | Playoffs | ✅ | presenter_playoffs.PNG |
| — | Breaking news | ❌ | presenter_breaking.PNG |
| — | Con tablet | ❌ | presenter_tablet.PNG |
| — | Debate | ❌ | presenter_debate.PNG |
| — | Reacción viral | ❌ | presenter_reaction.PNG |
| — | Récord histórico | ❌ | presenter_record.PNG |
| — | Predicción | ❌ | presenter_prediction.PNG |
| — | Cierre reel | ❌ | presenter_closing.PNG |

---

## DEFAULT

Camiseta por defecto (sin equipo reconocido):
```
black t-shirt with bold red number 7, diagonal red-white-red stripe, Dos Aros brand
```

---

## Naming convention

- NBA: `nba_CODIGO.PNG` — ej. `nba_GSW.PNG`
- Euroliga: `euro_CODIGO.PNG` — ej. `euro_MAD.PNG`
- Presentador: `presenter_DESCRIPCION.PNG`
- Todos en `assets/avatars/`

## Notas

- Usar siempre `nba_LAL.PNG` como referencia de personaje en ImageFX
- Si la cara cambia al regenerar: añadir al inicio `"IMPORTANT: Keep exact same face, bald head, short gray beard, same person as reference"`
- EA7 Milan (`MIL_EURO`) tiene código alternativo para evitar colisión con Milwaukee Bucks (`MIL`) en el diccionario Python
