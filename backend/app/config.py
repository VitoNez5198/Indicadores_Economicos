import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env en la carpeta raíz del backend
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

class Config:
    """Configuración de la aplicación cargada desde variables de entorno"""
    
    # Base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'indicadores_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # APIs externas
    MINDICADOR_API_URL = os.getenv('MINDICADOR_API_URL', 'https://mindicador.cl/api')
    
    # Scheduler
    ETL_INTERVAL_HOURS = int(os.getenv('ETL_INTERVAL_HOURS', 24))

