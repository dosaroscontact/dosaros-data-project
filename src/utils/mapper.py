import pandas as pd

def normalize_coordinates(val, max_val=100):
    """
    Normaliza coordenadas a escala 0-100.
    La Euroliga suele enviar 0-100 en su API moderna, 
    pero esto asegura consistencia.
    """
    try:
        return round((float(val) / float(max_val)) * 100, 2)
    except (ValueError, TypeError):
        return None

def map_euro_to_canonical(df, data_type="pbp"):
    """
    Traduce las columnas de Euroleague API al estándar Dos Aros.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if data_type == "pbp":
        # Mapeo según la librería euroleague-api y tu DB
        mapping = {
            'NUMBER': 'event_num',
            'PERIOD': 'period',
            'MARKERTIME': 'clock',
            'PLAYTYPE': 'action_type',
            'PLAYER_ID': 'player_id',
            'COORD_X': 'x',
            'COORD_Y': 'y'
        }
        
        # Renombramos solo las columnas que existan en el DF
        df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
        
        # Aplicamos normalización si hay coordenadas
        if 'x' in df.columns:
            df['x'] = df['x'].apply(lambda v: normalize_coordinates(v))
        if 'y' in df.columns:
            df['y'] = df['y'].apply(lambda v: normalize_coordinates(v))
            
    return df