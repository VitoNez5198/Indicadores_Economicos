from datetime import datetime, timedelta
import requests
import json
from app.config import Config
from app.utils.logger import setup_logger

# Configurar logger para este módulo
logger = setup_logger('extractor')

# Definir llaves de metadata que no son indicadores
METADATA_KEYS = ["version", "autor", "fecha"]

def fetch_all_indicators():
    """
    Se conecta a la API de Mindicador y obtiene todos los indicadores.
    
    Filtra la metadata (version, autor, fecha) y devuelve
    un diccionario solo con los datos de los indicadores.
    
    Retorna:
        dict: Un diccionario donde cada llave es un indicador (ej: 'dolar')
            y su valor es otro diccionario con sus detalles.
        None: Si ocurre un error en la extracción.
    """
    api_url = Config.MINDICADOR_API_URL
    logger.info(f"Iniciando extracción de datos desde: {api_url}")

    try:
        # Hacemos el request con un timeout de 10 segundos
        response = requests.get(api_url, timeout=10)
        
        # Verificar si la respuesta fue exitosa (código 200)
        response.raise_for_status() 
        
        logger.info("Datos extraídos exitosamente.")
        
        # Convertir la respuesta a JSON
        data = response.json()
        
        # Filtrar la metadata y devolver solo los indicadores
        indicators_data = {
            key: value for key, value in data.items() 
            if key not in METADATA_KEYS and isinstance(value, dict)
        }
        
        if not indicators_data:
            logger.warning("La API no devolvió indicadores, solo metadata.")
            return None
            
        return indicators_data

    except Exception as e:
        logger.error(f"Error inesperado en el extractor: {e}", exc_info=True)
        return None


def fetch_indicator_history(indicator_code, days=90):
    """
    Obtiene el histórico de un indicador específico.
    
    Args:
        indicator_code (str): Código del indicador ('dolar', 'uf', etc.)
        days (int): Cantidad de días hacia atrás (máximo 365)
    
    Returns:
        list: Lista de diccionarios con 'fecha' y 'valor'
        None: Si ocurre un error
    """
    api_url = f"{Config.MINDICADOR_API_URL}/{indicator_code}"
    logger.info(f"Obteniendo histórico de '{indicator_code}' ({days} días)")
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # La API devuelve el histórico en data['serie']
        if 'serie' not in data:
            logger.warning(f"No se encontró 'serie' para {indicator_code}")
            return None
        
        # Filtrar solo los últimos X días
        cutoff_date = datetime.now() - timedelta(days=days)
        
        historical_values = []
        for entry in data['serie']:
            entry_date = datetime.fromisoformat(entry['fecha'].replace('Z', '+00:00'))
            
            if entry_date >= cutoff_date:
                historical_values.append({
                    'fecha': entry['fecha'],
                    'valor': entry['valor']
                })
        
        logger.info(f"Se obtuvieron {len(historical_values)} registros históricos de '{indicator_code}'")
        return historical_values
        
    except Exception as e:
        logger.error(f"Error obteniendo histórico de {indicator_code}: {e}", exc_info=True)
        return None


def fetch_all_indicators_with_history(days=90):
    """
    Obtiene todos los indicadores con su histórico.
    
    Returns:
        dict: {
            'dolar': [{'fecha': '...', 'valor': 950}, ...],
            'uf': [{'fecha': '...', 'valor': 37500}, ...],
            ...
        }
    """
    # Primero obtener lista de indicadores disponibles
    current_indicators = fetch_all_indicators()
    
    if not current_indicators:
        return None
    
    all_history = {}
    
    # Para cada indicador, obtener su histórico
    for code in current_indicators.keys():
        history = fetch_indicator_history(code, days)
        if history:
            all_history[code] = history
    
    return all_history


# --- Bloque de Auto-Test ---
# Esto se ejecutará solo cuando corras el archivo directamente
# (ej: python app/services/extractor.py)
if __name__ == "__main__":
    print("Probando extractor con histórico...")
    
    # Probar un solo indicador
    dolar_history = fetch_indicator_history('dolar', days=30)
    
    if dolar_history:
        print(f"\n✓ Se obtuvieron {len(dolar_history)} registros del dólar")
        print("\nPrimeros 3 registros:")
        for entry in dolar_history[:3]:
            print(f"  Fecha: {entry['fecha']}, Valor: {entry['valor']}")
    else:
        print("\n✗ No se pudo obtener el histórico")