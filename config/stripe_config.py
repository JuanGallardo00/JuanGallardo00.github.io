"""
Configuración e inicialización segura de Stripe
"""
import os
import stripe
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def init_stripe():
    """
    Inicializa Stripe con la clave secreta desde variables de entorno
    
    Returns:
        bool: True si la inicialización fue exitosa, False en caso contrario
    """
    try:
        stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')

        if not stripe_secret_key:
            print("WARNING: STRIPE_SECRET_KEY no encontrada en variables de entorno")
            return False

        # Configurar la clave API de Stripe
        stripe.api_key = stripe_secret_key

        # Verificar que la clave funciona (opcional)
        try:
            stripe.Account.retrieve()
            print("Stripe inicializado correctamente")
            return True
        except stripe._error.AuthenticationError:
            print("ERROR: Clave de Stripe invalida")
            return False

    except Exception as e:
        print(f"ERROR al inicializar Stripe: {str(e)}")
        return False


def get_stripe_public_key():
    """
    Obtiene la clave pública de Stripe
    
    Returns:
        str: Clave pública de Stripe o None si no está configurada
    """
    return os.getenv('STRIPE_PUBLIC_KEY')


def get_webhook_secret():
    """
    Obtiene el secreto del webhook de Stripe
    
    Returns:
        str: Secreto del webhook o None si no está configurado
    """
    return os.getenv('WEBHOOK_SECRET')
