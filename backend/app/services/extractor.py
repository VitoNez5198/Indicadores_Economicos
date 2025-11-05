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

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexión al intentar acceder a la API: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout al esperar respuesta de la API: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP: {e.status_code} - {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar la respuesta JSON de la API: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en el extractor: {e}", exc_info=True)
        return None

# --- Bloque de Auto-Test ---
# Esto se ejecutará solo cuando corras el archivo directamente
# (ej: python app/services/extractor.py)
if __name__ == "__main__":
    
    print("Iniciando prueba del Extractor...")
    extracted_data = fetch_all_indicators()
    
    if extracted_data:
        print(f"\n[ÉXITO] Se extrajeron {len(extracted_data)} indicadores.")
        
        # Imprimir los primeros 2 para verificar
        print("\n--- Muestra de datos ---")
        count = 0
        for code, details in extracted_data.items():
            if count < 2:
                print(f"Código: {code}")
                print(f"  Nombre: {details.get('nombre')}")
                print(f"  Valor: {details.get('valor')}")
                print(f"  Unidad: {details.get('unidad_medida')}")
                print("-" * 20)
            count += 1
    else:
        print("\n[FALLO] No se pudieron extraer los datos.")