from flask import Flask
from .config import Config
from .firebase_init import init_firebase


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config.from_object(Config)

    init_firebase(app.config['FIREBASE_CREDENTIALS'], app.config['FIREBASE_DATABASE_URL'])

    from .routes.auth_routes import auth_bp
    from .routes.empleados import empleados_bp
    from .routes.registros import registros_bp
    from .routes.nomina import nomina_bp
    from .routes.usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(empleados_bp, url_prefix='/empleados')
    app.register_blueprint(registros_bp, url_prefix='/registros')
    app.register_blueprint(nomina_bp, url_prefix='/nomina')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

    from flask import session

    @app.context_processor
    def inject_session():
        return {'current_user': session}

    return app
