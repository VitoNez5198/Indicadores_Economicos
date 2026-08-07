from app.config import Config
from app.utils.logger import setup_logger

def test_config():
    """Probar que la configuración funciona"""
    logger = setup_logger('test')
    
    logger.info(f"Database Target: postgresql://{Config.DB_USER}:***@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    logger.info(f"API URL: {Config.MINDICADOR_API_URL}")
    logger.info(f"Debug Mode: {Config.DEBUG}")
    logger.info("✓ Configuración OK")

if __name__ == "__main__":
    test_config()