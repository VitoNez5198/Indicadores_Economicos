import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config

# Inicializar SQLAlchemy para que pueda ser importado por los modelos
# Aún no está "conectado" a la app, eso pasa en create_app
db = SQLAlchemy()

def create_app():
    """
    Factory function para crear la instancia de la aplicación Flask.
    """
    app = Flask(__name__)
    
    # Cargar la configuración desde la clase Config
    app.config.from_object(Config)
    
    # Inicializar las extensiones con la app
    db.init_app(app)
    CORS(app) # Habilitar CORS para todas las rutas

    # --- Registrar Blueprints (nuestras rutas de la API) ---
    # Lo haremos más adelante, pero dejamos el espacio
    with app.app_context():
        from .api import routes  # Importar rutas
        app.register_blueprint(routes.api_bp, url_prefix='/api')
        
        # Opcional: Crear tablas si no existen
        # En un proyecto más grande, se usaría Alembic (migraciones)
        # db.create_all() 

    return app