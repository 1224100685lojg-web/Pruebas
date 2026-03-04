from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)

    # ✅ Cargar config (normal o testing)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    Swagger(app)

    # ✅ Importar blueprints SOLO aquí
    from .routes import main_bp
    from .routes.estudiante import estudiantes_bp
    from .routes.materias import materias_bp
    from .routes.calificaciones import calificaciones_bp
    from .routes.auth import auth_bp

    # ✅ Registrar blueprints SOLO una vez
    app.register_blueprint(main_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(materias_bp)
    app.register_blueprint(calificaciones_bp)
    app.register_blueprint(auth_bp)

    return app