"""
Punto de entrada principal para la aplicación CV-DocConvert
"""
import os
from app import create_app
from config import init_stripe
from werkzeug.serving import WSGIRequestHandler

# Ocultar la versión del servidor en Werkzeug
WSGIRequestHandler.server_version = "WebServer"
WSGIRequestHandler.sys_version = ""

# Obtener el entorno de Flask
env = os.getenv('FLASK_ENV', 'development')

# Crear la aplicación Flask
app = create_app(env)

# Inicializar Stripe
init_stripe()

if __name__ == '__main__':
    # Configuración del servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = env == 'development'
    
    print(f"""
============================================================
         CV + DocConvert - Servidor iniciado
============================================================
  Entorno: {env.upper()}
  Host: {host}
  Puerto: {port}
  Debug: {str(debug)}
============================================================
    """)
    
    # Iniciar el servidor
    app.run(host=host, port=port, debug=debug)
