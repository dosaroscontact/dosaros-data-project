import pandas as pd

def normalize_euro_coords(x, y):
    """
    La Euroliga usa un canvas donde el centro es (0,0) o 
    un sistema de 0-100. Este mapper asegura el estándar Dos Aros.
    """
    try:
        # La API de Euroliga moderna suele enviar COORD_X en rango aprox -250 a 250
        # y COORD_Y de 0 a 1400. Normalizamos a escala 0-100 para consistencia.
        norm_x = ((float(x) + 250) / 500) * 100
        norm_y = (float(y) / 1400) * 100
        return round(norm_x, 2), round(norm_y, 2)
    except:
        return None, None

def map_euro_to_canonical(df, data_type="pbp"):
    if df is None or df.empty:
        return pd.DataFrame()

    if data_type == "pbp":
        mapping = {
            'NUMBER': 'event_num',
            'PERIOD': 'period',
            'MARKERTIME': 'clock',
            'PLAYTYPE': 'action_type',
            'PLAYER_ID': 'player_id',
            'COORD_X': 'x',
            'COORD_Y': 'y'
        }
        
        df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
        
        # Normalización matemática de la pista
        if 'x' in df.columns and 'y' in df.columns:
            coords = df.apply(lambda row: normalize_euro_coords(row['x'], row['y']), axis=1)
            df['x_norm'], df['y_norm'] = zip(*coords)
            
        return df