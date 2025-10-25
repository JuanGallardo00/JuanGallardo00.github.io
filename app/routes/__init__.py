"""
Módulo de rutas de la aplicación CV-DocConvert
"""

from .main_routes import main_bp
from .convert_routes import convert_bp
from .stripe_routes import stripe_bp

__all__ = ['main_bp', 'convert_bp', 'stripe_bp']
