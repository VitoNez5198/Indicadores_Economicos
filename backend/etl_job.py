import sys
import os

# Añadir el directorio 'app' al path de Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
# Importamos las funciones SIMPLES
from app.services.extractor import fetch_indicator_history
from app.services.transformer import transform_historical_data
from app.services.loader import load_data
from app.utils.logger import setup_logger

logger = setup_logger('etl_job')

# LISTA DE INDICADORES QUE QUEREMOS PROCESAR
# (Estos deben coincidir con los 'code' en tu tabla 'indicators')
INDICATORS_TO_PROCESS = [
    'dolar',
    'uf',
    'euro',
    'utm',
    'ipc',
    'bitcoin'
]

def run_etl():
    """
    Orquesta el proceso completo de ETL:
    Itera sobre cada indicador, extrae su historial,
    lo transforma y lo carga en la DB.
    """
    logger.info("=============================================")
    logger.info("INICIANDO PROCESO ETL HISTÓRICO...")
    logger.info(f"Se procesarán {len(INDICATORS_TO_PROCESS)} indicadores.")
    logger.info("=============================================")

    total_records_loaded = 0
    total_records_failed = 0

    # Bucle principal: 1 indicador a la vez
    for indicator_code in INDICATORS_TO_PROCESS:
        
        logger.info(f"--- Procesando: {indicator_code.upper()} ---")

        # Paso 1: Extraer
        # Llama a la función simple
        raw_data = fetch_indicator_history(indicator_code)
        
        if not raw_data:
            logger.error(f"Extracción fallida para '{indicator_code}'. Saltando al siguiente.")
            total_records_failed += 1
            continue

        # Paso 2: Transformar
        # Llama a la función simple
        clean_data = transform_historical_data(raw_data)
        
        if not clean_data:
            logger.error(f"Transformación fallida para '{indicator_code}'. Saltando al siguiente.")
            total_records_failed += 1
            continue
            
        # Paso 3: Cargar
        # El loader.py no necesita cambios, ¡recibirá los datos!
        try:
            # El loader SÍ necesita el contexto de la app
            # (El loader nos dirá cuántos cargó, cuántos omitió)
            load_data(clean_data)
            total_records_loaded += len(clean_data) # Esto es aprox, el loader es más exacto
            logger.info(f"Proceso de carga finalizado para '{indicator_code}'.")
        except Exception as e:
            logger.error(f"Error crítico durante la fase de carga de '{indicator_code}': {e}", exc_info=True)
            total_records_failed += 1
            
        logger.info(f"--- Fin de {indicator_code.upper()} ---")

    logger.info("=============================================")
    logger.info("PROCESO ETL HISTÓRICO FINALIZADO.")
    logger.info(f"Total de indicadores procesados con éxito (aprox): {len(INDICATORS_TO_PROCESS) - total_records_failed}")
    logger.info(f"Total de indicadores fallidos: {total_records_failed}")
    logger.info("=============================================")

# --- Punto de entrada principal ---
if __name__ == "__main__":
    
    logger.info("Creando contexto de aplicación Flask para el ETL...")
    
    app = create_app()
    
    with app.app_context():
        run_etl()