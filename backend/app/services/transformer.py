import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.utils.logger import setup_logger
from app.services.extractor import fetch_all_indicators

# Configurar logger para este módulo
logger = setup_logger('transformer')

def transform_data(raw_data: dict) -> list:
    """
    Transforma los datos crudos del extractor en una lista
    de diccionarios limpios, listos para el 'loader'.
    
    Args:
        raw_data (dict): El diccionario crudo de fetch_all_indicators().
                         Ej: {'dolar': {'valor': 123.45, 'fecha': '...'}, ...}

    Returns:
        list: Lista de diccionarios limpios.
              Ej: [{'code': 'dolar', 'value': Decimal('123.45'), 'date': date(2025, 11, 5)}, ...]
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
            value_str = str(details['valor']).replace('.', '').replace(',', '.')
            value = Decimal(str(details['valor']))

            # 3. Transformar 'fecha' a objeto date
            # El formato de la API es ISO 8601 (ej: "2025-11-05T14:00:00.000Z")
            date_iso = details['fecha']
            date = datetime.fromisoformat(date_iso.replace('Z', '+00:00')).date()

            # 4. Crear el diccionario limpio
            clean_item = {
                'code': code,
                'value': value,
                'date': date
            }
            transformed_list.append(clean_item)

        except InvalidOperation as e:
            logger.error(f"Error al convertir valor '{details.get('valor')}' a Decimal para '{code}': {e}")
        except ValueError as e:
            logger.error(f"Error al convertir fecha '{details.get('fecha')}' a Date para '{code}': {e}")
        except Exception as e:
            logger.error(f"Error inesperado transformando '{code}': {e}", exc_info=True)

    logger.info(f"Transformación completada. {len(transformed_list)} indicadores listos para cargar.")
    return transformed_list

# --- Bloque de Auto-Test ---
# Esto se ejecutará solo cuando corras el archivo directamente
if __name__ == "__main__":
    
    print("Iniciando prueba del Transformador (depende del Extractor)...")
    
    # 1. Extraer datos (como hicimos antes)
    print("\n--- Paso 1: Extrayendo Datos ---")
    raw_data = fetch_all_indicators()
    
    if not raw_data:
        print("[FALLO] El extractor no pudo obtener datos.")
    else:
        print(f"[ÉXITO] Extractor obtuvo {len(raw_data)} indicadores.")
        
        # 2. Transformar los datos
        print("\n--- Paso 2: Transformando Datos ---")
        clean_data = transform_data(raw_data)
        
        if clean_data:
            print(f"[ÉXITO] Se transformaron {len(clean_data)} indicadores.")
            
            # Imprimir el primero para verificar
            print("\n--- Muestra de datos transformados ---")
            first_item = clean_data[0]
            print(f"  Código: {first_item['code']}")
            print(f"  Valor: {first_item['value']} (Tipo: {type(first_item['value'])})")
            print(f"  Fecha: {first_item['date']} (Tipo: {type(first_item['date'])})")
            print("-" * 20)
        else:
            print("\n[FALLO] No se pudieron transformar los datos.")