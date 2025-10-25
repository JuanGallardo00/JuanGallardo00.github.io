"""
Módulo de configuración del proyecto CV-DocConvert
"""

from .settings import Config
from .stripe_config import init_stripe

__all__ = ['Config', 'init_stripe']
