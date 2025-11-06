import requests
import json
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger('extractor')

# OJO: La URL base ahora termina en /
MINDICADOR_API_BASE_URL = Config.MINDICADOR_API_URL.rstrip('/') + '/'

def fetch_indicator_history(indicator_code: str) -> dict:
    """
    Se conecta a la API de Mindicador y obtiene el historial
    COMPLETO de un indicador específico.
    
    Args:
        indicator_code (str): El código del indicador (ej: 'dolar', 'uf')

    Retorna:
        dict: Un diccionario con los datos del indicador, o None si falla.
              Ej: {'codigo': 'dolar', 'nombre': '...', 'serie': [{'fecha': '...', 'valor': ...}, ...]}
    """
    api_url = f"{MINDICADOR_API_BASE_URL}{indicator_code}"
    logger.info(f"Iniciando extracción de historial para '{indicator_code}' desde: {api_url}")

    try:
        response = requests.get(api_url, timeout=20) # Timeout más largo para historial
        response.raise_for_status()
        
        data = response.json()
        
        # Validar que la respuesta tenga la data histórica
        if 'serie' not in data or not data['serie']:
            logger.warning(f"Respuesta de API para '{indicator_code}' no contiene 'serie' de datos.")
            return None
            
        logger.info(f"Datos históricos de '{indicator_code}' extraídos exitosamente.")
        return data

    except requests.exceptions.HTTPError as e:
        # Si la API devuelve 404 (ej: 'bitcoin' no tiene historial por año)
        if e.response.status_code == 404:
            logger.warning(f"API devolvió 404 para '{indicator_code}'. El indicador puede no existir.")
            return None
        logger.error(f"Error HTTP para '{indicator_code}': {e.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en extractor para '{indicator_code}': {e}", exc_info=True)
        return None

# --- Bloque de Auto-Test ---
if __name__ == "__main__":
    
    print("Iniciando prueba del Extractor (histórico)...")
    code_to_test = 'dolar'
    extracted_data = fetch_indicator_history(code_to_test)
    
    if extracted_data:
        print(f"\n[ÉXITO] Se extrajo el historial de '{code_to_test}'.")
        print(f"Nombre: {extracted_data.get('nombre')}")
        print(f"Total de registros históricos: {len(extracted_data.get('serie', []))}")
        
        print("\n--- Muestra de datos (primer registro) ---")
        if extracted_data.get('serie'):
            first_entry = extracted_data['serie'][0]
            print(f"  Fecha: {first_entry.get('fecha')}")
            print(f"  Valor: {first_entry.get('valor')}")
    else:
        print(f"\n[FALLO] No se pudo extraer el historial de '{code_to_test}'.")