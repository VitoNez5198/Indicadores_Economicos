from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.utils.logger import setup_logger
from app.services.extractor import fetch_all_indicators

# Configurar logger para este módulo
logger = setup_logger('transformer')

def transform_data(raw_data: dict) -> list:
    """
    Transforma los datos crudos (solo valores actuales)
    """
    transformed_list = []
    
    if not raw_data or not isinstance(raw_data, dict):
        logger.warning("No se recibieron datos crudos para transformar.")
        return transformed_list

    logger.info(f"Transformando {len(raw_data)} indicadores...")

    for code, details in raw_data.items():
        try:
            # 1. Validar que 'valor' y 'fecha' existan
            if 'valor' not in details or 'fecha' not in details:
                logger.warning(f"Datos incompletos para '{code}'. Saltando.")
                continue

            # 2. Transformar 'valor' a Decimal
            # El valor puede venir como string con coma (ej: "37.500,50")
            # Lo limpiamos: quitamos puntos (miles) y cambiamos coma por punto (decimal)
            value = Decimal(str(details['valor']))
            date_iso = details['fecha']
            date = datetime.fromisoformat(date_iso.replace('Z', '+00:00')).date()

            clean_item = {
                'code': code,
                'value': value,
                'date': date
            }
            transformed_list.append(clean_item)

        except Exception as e:
            logger.error(f"Error inesperado transformando '{code}': {e}", exc_info=True)

    logger.info(f"Transformación completada. {len(transformed_list)} indicadores listos para cargar.")
    return transformed_list

def transform_historical_data(historical_data: dict) -> list:
    """
    Transforma datos históricos de múltiples indicadores.
    
    Args:
        historical_data: {
            'dolar': [{'fecha': '...', 'valor': 950}, ...],
            'uf': [{'fecha': '...', 'valor': 37500}, ...]
        }
    
    Returns:
        list: [
            {'code': 'dolar', 'value': Decimal('950'), 'date': date(...)},
            ...
        ]
    """
    transformed_list = []
    
    if not historical_data:
        logger.warning("No hay datos históricos para transformar")
        return transformed_list
    
    logger.info(f"Transformando histórico de {len(historical_data)} indicadores...")
    
    for code, history in historical_data.items():
        for entry in history:
            try:
                value = Decimal(str(entry['valor']))
                date_iso = entry['fecha']
                date = datetime.fromisoformat(date_iso.replace('Z', '+00:00')).date()
                
                clean_item = {
                    'code': code,
                    'value': value,
                    'date': date
                }
                transformed_list.append(clean_item)
                
            except Exception as e:
                logger.error(f"Error transformando entrada de '{code}': {e}")
                continue
    
    logger.info(f"Transformación histórica completada. {len(transformed_list)} registros listos.")
    return transformed_list
# --- Bloque de Auto-Test ---
# Esto se ejecutará solo cuando corras el archivo directamente
if __name__ == "__main__":
    from app.services.extractor import fetch_all_indicators_with_history
    
    print("Probando transformer con histórico...")
    
    raw_data = fetch_all_indicators_with_history(days=7)
    
    if raw_data:
        clean_data = transform_historical_data(raw_data)
        print(f"\n✓ Se transformaron {len(clean_data)} registros")
        print("\nPrimeros 3 registros:")
        for item in clean_data[:3]:
            print(f"  {item['code']}: ${item['value']} ({item['date']})")
    else:
        print("\n✗ No se pudieron obtener datos")