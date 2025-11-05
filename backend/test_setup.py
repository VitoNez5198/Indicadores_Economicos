from app.config import Config
from app.utils.logger import setup_logger

def test_config():
    """Probar que la configuración funciona"""
    logger = setup_logger('test')
    
    logger.info("=== Probando Configuración ===")
    logger.info(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
    logger.info(f"API URL: {Config.MINDICADOR_API_URL}")
    logger.info(f"Debug Mode: {Config.DEBUG}")
    logger.info("✓ Configuración OK")

if __name__ == "__main__":
    test_config()