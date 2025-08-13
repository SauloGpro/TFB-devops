# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargamos .env si existe (opcional)
load_dotenv()

db = SQLAlchemy()

def create_app(env_name: str = "development"):
    """Factory to create Flask app."""
    app = Flask(__name__)

    # Cargamos configuración por defecto desde tus clases en app/config.py
    # (config_dict debería existir en app/config.py tal y como lo tienes)
    from app.config import config_dict
    app.config.from_object(config_dict.get(env_name, config_dict["development"]))

    # Si hay DATABASE_URI en las variables de entorno, la usamos (override)
    database_uri = os.getenv("DATABASE_URI")
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    # Inicializamos extensiones
    db.init_app(app)

    # Registramos blueprints *aquí* para evitar import cycles
    from app.routes import data_routes
    app.register_blueprint(data_routes)

    return app
