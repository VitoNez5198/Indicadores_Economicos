from flask import Blueprint, jsonify, request
from sqlalchemy import desc, func, text  # <-- 'text' es necesario
from app import get_db
from app.models import Indicator, IndicatorValue
from app.utils.logger import setup_logger
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)
logger = setup_logger('api')

@api_bp.route('/indicators', methods=['GET'])
def get_indicators():
    """Obtener todos los indicadores con su último valor"""
    try:
        db = get_db()
        
        # Query para obtener indicadores con su último valor
        indicators = db.query(
            Indicator.id,
            Indicator.code,
            Indicator.name,
            Indicator.unit,
            IndicatorValue.value,
            IndicatorValue.date
        ).outerjoin(
            IndicatorValue,
            Indicator.id == IndicatorValue.indicator_id
        ).distinct(
            Indicator.id
        ).order_by(
            Indicator.id,
            desc(IndicatorValue.date)
        ).all()
        
        result = []
        for ind in indicators:
            result.append({
                'id': ind.id,
                'code': ind.code,
                'name': ind.name,
                'unit': ind.unit,
                'latest_value': float(ind.value) if ind.value else None,
                'latest_date': ind.date.isoformat() if ind.date else None
            })
        
        db.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error en get_indicators: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators/<code>', methods=['GET'])
def get_indicator_by_code(code):
    """Obtener un indicador específico por código"""
    try:
        db = get_db()
        
        indicator = db.query(Indicator).filter(Indicator.code == code).first()
        
        if not indicator:
            db.close()
            return jsonify({'error': 'Indicador no encontrado'}), 404
        
        # Obtener último valor
        latest_value = db.query(IndicatorValue)\
            .filter(IndicatorValue.indicator_id == indicator.id)\
            .order_by(desc(IndicatorValue.date))\
            .first()
        
        result = {
            'id': indicator.id,
            'code': indicator.code,
            'name': indicator.name,
            'unit': indicator.unit,
            'latest_value': float(latest_value.value) if latest_value else None,
            'latest_date': latest_value.date.isoformat() if latest_value else None
        }
        
        db.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error en get_indicator_by_code: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators/<code>/history', methods=['GET'])
def get_indicator_history(code):
    """Obtener histórico de un indicador"""
    try:
        db = get_db()
        
        # Parámetros opcionales
        days = request.args.get('days', default=30, type=int)
        limit = request.args.get('limit', default=100, type=int)
        
        # Buscar indicador
        indicator = db.query(Indicator).filter(Indicator.code == code).first()
        
        if not indicator:
            db.close()
            return jsonify({'error': 'Indicador no encontrado'}), 404
        
        # Calcular fecha desde
        date_from = datetime.now().date() - timedelta(days=days)
        
        # Query de valores
        values = db.query(IndicatorValue)\
            .filter(
                IndicatorValue.indicator_id == indicator.id,
                IndicatorValue.date >= date_from
            )\
            .order_by(desc(IndicatorValue.date))\
            .limit(limit)\
            .all()
        
        result = {
            'indicator': {
                'code': indicator.code,
                'name': indicator.name,
                'unit': indicator.unit
            },
            'values': [
                {
                    'value': float(v.value),
                    'date': v.date.isoformat()
                }
                for v in values
            ],
            'count': len(values)
        }
        
        db.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error en get_indicator_history: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats/latest', methods=['GET'])
def get_latest_stats():
    """Obtener estadísticas de los últimos valores"""
    try:
        db = get_db()
        
        # Subquery para obtener el último valor de cada indicador
        subq = db.query(
            IndicatorValue.indicator_id,
            func.max(IndicatorValue.date).label('max_date')
        ).group_by(IndicatorValue.indicator_id).subquery()
        
        # Query principal
        latest = db.query(
            Indicator.code,
            Indicator.name,
            Indicator.unit,
            IndicatorValue.value,
            IndicatorValue.date
        ).join(
            IndicatorValue,
            Indicator.id == IndicatorValue.indicator_id
        ).join(
            subq,
            (IndicatorValue.indicator_id == subq.c.indicator_id) &
            (IndicatorValue.date == subq.c.max_date)
        ).all()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'indicators': [
                {
                    'code': item.code,
                    'name': item.name,
                    'unit': item.unit,
                    'value': float(item.value),
                    'date': item.date.isoformat()
                }
                for item in latest
            ],
            'count': len(latest)
        }
        
        db.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error en get_latest_stats: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para verificar que la API está funcionando"""
    try:
        db = get_db()
        # Probar conexión a DB
        # AQUÍ ESTÁ EL ARREGLO:
        db.execute(text('SELECT 1'))
        db.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        # El error ahora será capturado aquí si falla
        logger.error(f"Error en health_check: {e}") 
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500