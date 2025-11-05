import sys
import os

# Añadir el directorio 'app' al path de Python
# Esto es necesario para que el script (etl_job.py) pueda encontrar
# los módulos 'app.services', 'app.models', etc.,
# al ser ejecutado directamente desde la carpeta 'backend'.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app, get_db
from app.services.extractor import fetch_all_indicators
from app.services.transformer import transform_data
from app.services.loader import load_data
from app.utils.logger import setup_logger

# Configurar logger para este módulo
logger = setup_logger('etl_job')

def run_etl():
    """
    Orquesta el proceso completo de ETL:
    1. Extrae datos de la API.
    2. Transforma los datos.
    3. Carga los datos en la base de datos.
    """
    logger.info("=============================================")
    logger.info("INICIANDO PROCESO ETL DE INDICADORES...")
    logger.info("=============================================")

    # Paso 1: Extraer
    logger.info("--- PASO 1: EXTRACCIÓN ---")
    raw_data = fetch_all_indicators()
    
    if not raw_data:
        logger.error("Extracción fallida. Abortando ETL.")
        return

    logger.info(f"Extracción exitosa. {len(raw_data)} indicadores recibidos.")

    # Paso 2: Transformar
    logger.info("--- PASO 2: TRANSFORMACIÓN ---")
    clean_data = transform_data(raw_data)
    
    if not clean_data:
        logger.error("Transformación fallida o no generó datos. Abortando ETL.")
        return
        
    logger.info(f"Transformación exitosa. {len(clean_data)} registros listos.")

    # Paso 3: Cargar
    logger.info("--- PASO 3: CARGA (LOAD) ---")
    try:
        load_data(clean_data)
        logger.info("Proceso de carga finalizado.")
    except Exception as e:
        logger.error(f"Error crítico durante la fase de carga: {e}", exc_info=True)
        
    logger.info("=============================================")
    logger.info("PROCESO ETL FINALIZADO.")
    logger.info("=============================================")

# --- Punto de entrada principal ---
if __name__ == "__main__":
    
    logger.info("Creando contexto de aplicación Flask para el ETL...")
    
    # Creamos una instancia de la app para tener el contexto
    app = create_app()
    
    # 'app_context()' es VITAL.
    # Empuja el contexto de la aplicación para que get_db()
    # y SQLAlchemy sepan a qué base de datos conectarse.
    with app.app_context():
        # Ahora que estamos "dentro" de la app, ejecutamos el ETL
        run_etl()