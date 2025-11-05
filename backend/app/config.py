import os
#from dotenv import load_dotenv

# Cargar variables de entorno
#load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Base de datos
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'indicadores_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'Trevor5198'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    SECRET_KEY = 'dev-secret-key'
    DEBUG = True
    
    # APIs externas
    MINDICADOR_API_URL = 'https://mindicador.cl/api'
    
    # Scheduler
    ETL_INTERVAL_HOURS = 24
