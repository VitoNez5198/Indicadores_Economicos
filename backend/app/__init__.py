from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.utils.logger import setup_logger

# Logger global
logger = setup_logger('app')

# Engine de SQLAlchemy (global)
engine = None
SessionLocal = None

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Habilitar CORS para el frontend
    CORS(app)
    
    # Inicializar base de datos
    init_db()
    
    # Registrar blueprints (rutas)
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Ruta de prueba
    @app.route('/')
    def index():
        return {
            'message': 'API de Indicadores Económicos',
            'status': 'running',
            'endpoints': {
                'indicators': '/api/indicators',
                'indicator_detail': '/api/indicators/<code>',
                'indicator_history': '/api/indicators/<code>/history',
                'latest': '/api/stats/latest'
            }
        }
    
    logger.info("✓ Aplicación Flask inicializada")
    return app

def init_db():
    """Inicializar conexión a la base de datos"""
    global engine, SessionLocal
    
    try:
        engine = create_engine(
            Config.SQLALCHEMY_DATABASE_URI,
            echo=Config.DEBUG,
            pool_pre_ping=True
        )
        
        SessionLocal = sessionmaker(bind=engine)
        
        # Probar conexión
        with engine.connect() as conn:
            logger.info("✓ Conexión a PostgreSQL exitosa")
            
    except Exception as e:
        logger.error(f"✗ Error conectando a PostgreSQL: {e}")
        raise

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass