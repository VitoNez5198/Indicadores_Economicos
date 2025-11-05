from app import create_app
from app.utils.logger import setup_logger

logger = setup_logger('run')

if __name__ == '__main__':
    try:
        app = create_app()
        logger.info("=" * 50)
        logger.info("Iniciando servidor Flask...")
        logger.info("URL: http://localhost:5000")
        logger.info("Presiona CTRL+C para detener")
        logger.info("=" * 50)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        raise