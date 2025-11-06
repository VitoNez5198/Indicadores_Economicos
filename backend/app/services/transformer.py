import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.utils.logger import setup_logger
from app.services.extractor import fetch_indicator_history # Importamos el extractor simple

logger = setup_logger('transformer')

def transform_historical_data(raw_data: dict) -> list:
    """
    Transforma los datos crudos del historial de UN indicador
    en una lista de diccionarios limpios, listos para el 'loader'.
    
    Args:
        raw_data (dict): El diccionario crudo de fetch_indicator_history().
                         Ej: {'codigo': 'dolar', 'serie': [{'fecha': '...', 'valor': ...}]}

    Returns:
        list: Lista de diccionarios limpios.
              Ej: [{'code': 'dolar', 'value': Decimal('123.45'), 'date': date(...) }, ...]
    """
    transformed_list = []
    
    if not raw_data or 'serie' not in raw_data or 'codigo' not in raw_data:
        logger.warning("No se recibieron datos crudos o faltan 'serie'/'codigo' para transformar.")
        return transformed_list

    code = raw_data['codigo']
    historical_series = raw_data['serie']

    logger.info(f"Transformando {len(historical_series)} registros para '{code}'...")

    for entry in historical_series:
        try:
            # 1. Validar que 'valor' y 'fecha' existan
            if 'valor' not in entry or 'fecha' not in entry:
                logger.warning(f"Datos incompletos en la serie de '{code}'. Saltando registro.")
                continue

            # 2. Transformar 'valor' a Decimal
            # El valor viene como float o string, lo limpiamos
            value_str = str(entry['valor']).replace('.', '').replace(',', '.')
            
            # Re-insertar el punto decimal si era un string con coma (ej: 39623,18 -> 39623.18)
            # OJO: La API de mindicador es inconsistente. A veces usa float (950.5),
            # a veces usa string con coma (para la UF).
            # Esta lógica asume que si tiene coma, es un decimal.
            # Una lógica más robusta es la que te di antes:
            value_str_cleaned = str(entry['valor'])
            if ',' in value_str_cleaned:
                 # Es un string tipo "39.623,18" -> "39623.18"
                value_str_cleaned = value_str_cleaned.replace('.', '').replace(',', '.')
            
            value = Decimal(value_str_cleaned)

            # 3. Transformar 'fecha' a objeto date
            # El formato de la API es ISO 8601 (ej: "2024-10-27T03:00:00.000Z")
            date_iso = entry['fecha']
            date = datetime.fromisoformat(date_iso.replace('Z', '+00:00')).date()

            # 4. Crear el diccionario limpio
            clean_item = {
                'code': code,
                'value': value,
                'date': date
            }
            transformed_list.append(clean_item)

        except (InvalidOperation, ValueError, TypeError) as e:
            logger.error(f"Error al convertir valor '{entry.get('valor')}' o fecha '{entry.get('fecha')}' para '{code}': {e}")
        except Exception as e:
            logger.error(f"Error inesperado transformando '{code}': {e}", exc_info=True)

    logger.info(f"Transformación completada para '{code}'. {len(transformed_list)} registros listos.")
    return transformed_list

# --- Bloque de Auto-Test ---
if __name__ == "__main__":
    
    print("Iniciando prueba del Transformador (histórico)...")
    
    # 1. Extraer datos (como hicimos antes)
    print("\n--- Paso 1: Extrayendo Datos ('dolar') ---")
    raw_data = fetch_indicator_history('dolar')
    
    if not raw_data:
        print("[FALLO] El extractor no pudo obtener datos.")
    else:
        print(f"[ÉXITO] Extractor obtuvo {len(raw_data.get('serie',[]))} registros para 'dolar'.")
        
        # 2. Transformar los datos
        print("\n--- Paso 2: Transformando Datos ---")
        clean_data = transform_historical_data(raw_data)
        
        if clean_data:
            print(f"[ÉXITO] Se transformaron {len(clean_data)} registros.")
            
            # Imprimir el último (el más antiguo) para verificar
            print("\n--- Muestra de datos transformados (registro más antiguo) ---")
            last_item = clean_data[-1]
            print(f"  Código: {last_item['code']}")
            print(f"  Valor: {last_item['value']} (Tipo: {type(last_item['value'])})")
            print(f"  Fecha: {last_item['date']} (Tipo: {type(last_item['date'])})")
            print("-" * 20)
        else:
            print("\n[FALLO] No se pudieron transformar los datos.")