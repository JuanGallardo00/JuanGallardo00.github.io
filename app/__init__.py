"""
Módulo principal de la aplicación Flask CV-DocConvert
Utiliza el patrón Factory para crear la aplicación
"""
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.settings import config
import os

# Inicializar extensiones
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name='default'):
    """
    Factory pattern para crear la aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración a usar ('development', 'production', 'default')
    
    Returns:
        Flask: Aplicación Flask configurada
    """
    # Crear la instancia de Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones (CSRF deshabilitado temporalmente para desarrollo)
    # csrf.init_app(app)
    
    # Configurar CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True)
    
    # Inicializar Rate Limiter
    limiter.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Aplicar headers de seguridad
    apply_security_headers(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    return app


def register_blueprints(app):
    """
    Registra todos los blueprints de la aplicación
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    # Importar blueprints
    from app.routes.main_routes import main_bp
    from app.routes.convert_routes import convert_bp
    from app.routes.stripe_routes import stripe_bp
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(convert_bp, url_prefix='/convert')
    app.register_blueprint(stripe_bp, url_prefix='/stripe')

    print("Blueprints registrados correctamente")


def apply_security_headers(app):
    """
    Aplica headers de seguridad a todas las respuestas
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    @app.after_request
    def set_security_headers(response):
        # Ocultar versión del servidor - Eliminar completamente el header
        if 'Server' in response.headers:
            del response.headers['Server']

        # HSTS - HTTP Strict Transport Security
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Prevenir MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Protección XSS
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://js.stripe.com; "
            "style-src 'self' https://fonts.googleapis.com; "
            "img-src 'self' data:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src https://js.stripe.com https://hooks.stripe.com; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "upgrade-insecure-requests;"
        )
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response

    print("Headers de seguridad aplicados")


def register_error_handlers(app):
    """
    Registra manejadores de errores personalizados
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Error interno del servidor'}, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'error': 'Archivo demasiado grande. Máximo 16 MB'}, 413
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Demasiadas solicitudes. Por favor, espera un momento.'}, 429

    print("Manejadores de errores registrados")
