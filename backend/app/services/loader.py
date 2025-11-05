from app import get_db
from app.models import Indicator, IndicatorValue
from app.utils.logger import setup_logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

# Configurar logger para este módulo
logger = setup_logger('loader')

def load_data(clean_data: list):
    """
    Carga la lista de datos limpios en la base de datos PostgreSQL.
    Maneja duplicados y actualiza solo si es necesario.
    
    Args:
        clean_data (list): La lista de diccionarios limpios del transformador.
                           Ej: [{'code': 'dolar', 'value': Decimal('...'), 'date': date(...) }, ...]
    """
    
    # Este módulo NECESITA un contexto de Flask para acceder a get_db()
    # No puede ser probado con 'python -m', debe ser llamado por un script
    # que sí tenga acceso al contexto de la app (como etl_job.py)
    try:
        db = get_db()
        logger.info(f"Iniciando carga de {len(clean_data)} registros...")
    except Exception as e:
        logger.error(f"Error crítico al obtener la sesión de DB: {e}")
        logger.error("El Loader no puede funcionar sin un contexto de aplicación Flask.")
        return

    # --- Optimización: Cachear IDs de indicadores ---
    # Hacemos una sola consulta para traer todos los indicadores
    # y los guardamos en un dict para búsquedas rápidas en memoria.
    try:
        indicators_db = db.query(Indicator.id, Indicator.code).all()
        # Creamos un diccionario: {'dolar': 1, 'uf': 2, ...}
        indicator_id_map = {code: id for id, code in indicators_db}
    except Exception as e:
        logger.error(f"Error al cargar el mapa de indicadores desde la DB: {e}")
        db.close()
        return

    new_records_count = 0
    skipped_records_count = 0

    for item in clean_data:
        code = item['code']
        value = item['value']
        date = item['date']

        # 1. Buscar el ID del indicador en nuestro mapa
        indicator_id = indicator_id_map.get(code)
        
        if not indicator_id:
            # El indicador existe en la API pero no en nuestra tabla 'indicators'
            # (Ej: 'libra_cobre' que no agregamos en init.sql)
            logger.warning(f"Indicador '{code}' no encontrado en la tabla 'indicators'. Saltando.")
            continue

        try:
            # 2. Verificar si el registro ya existe (Upsert)
            # Buscamos un valor por ID de indicador y fecha
            existing_value = db.query(IndicatorValue).filter_by(
                indicator_id=indicator_id,
                date=date
            ).first()

            if existing_value:
                # El registro ya existe. Verificamos si el valor es el mismo.
                if existing_value.value == value:
                    # Mismo valor, no hacemos nada
                    skipped_records_count += 1
                else:
                    # El valor cambió (ej: corrección del Banco Central)
                    logger.info(f"Actualizando valor para '{code}' en fecha {date}.")
                    existing_value.value = value
                    new_records_count += 1 # Contamos como actualización
            else:
                # El registro no existe, lo creamos
                new_value = IndicatorValue(
                    indicator_id=indicator_id,
                    value=value,
                    date=date
                )
                db.add(new_value)
                new_records_count += 1
        
        except SQLAlchemyError as e:
            logger.error(f"Error de base de datos procesando '{code}' en {date}: {e}")
            db.rollback() # Revertir esta operación fallida
            continue # Continuar con el siguiente item

    # 3. Finalizar la transacción
    try:
        db.commit()
        logger.info("Carga de datos completada exitosamente.")
        logger.info(f"Registros nuevos/actualizados: {new_records_count}")
        logger.info(f"Registros omitidos (duplicados): {skipped_records_count}")
    except SQLAlchemyError as e:
        logger.error(f"Error al hacer commit final a la base de datos: {e}")
        db.rollback()
    finally:
        db.close()
        logger.info("Sesión de base de datos cerrada.")

# --- Bloque de Auto-Test ---
if __name__ == "__main__":
    logger.warning("Este módulo no se puede ejecutar directamente.")
    logger.warning("Depende de un contexto de aplicación Flask para acceder a la DB.")
    logger.warning("Ejecute 'python etl_job.py' en su lugar.")