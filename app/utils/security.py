"""
Utilidades de seguridad para la aplicación
Configuración de headers de seguridad y rate limiting
"""
from functools import wraps
from flask import request, jsonify
import re


def validate_filename(filename):
    """
    Valida que el nombre del archivo no contenga caracteres peligrosos

    Args:
        filename (str): Nombre del archivo a validar

    Returns:
        bool: True si el nombre es válido
    """
    # Permitir solo caracteres alfanuméricos, puntos, guiones y guiones bajos
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, filename))


def sanitize_filename(filename):
    """
    Sanitiza el nombre de un archivo

    Args:
        filename (str): Nombre del archivo

    Returns:
        str: Nombre sanitizado
    """
    # Eliminar caracteres peligrosos
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    # Eliminar múltiples puntos consecutivos
    sanitized = re.sub(r'\.+', '.', sanitized)
    return sanitized


def validate_file_extension(filename, allowed_extensions):
    """
    Valida que la extensión del archivo esté permitida

    Args:
        filename (str): Nombre del archivo
        allowed_extensions (set): Conjunto de extensiones permitidas

    Returns:
        bool: True si la extensión es válida
    """
    if '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def check_file_size(file_size, max_size=16*1024*1024):
    """
    Verifica que el tamaño del archivo no exceda el máximo

    Args:
        file_size (int): Tamaño del archivo en bytes
        max_size (int): Tamaño máximo permitido en bytes (default: 16MB)

    Returns:
        bool: True si el tamaño es válido
    """
    return 0 < file_size <= max_size


def validate_request_data(required_fields):
    """
    Decorador para validar que los campos requeridos estén presentes en la petición

    Args:
        required_fields (list): Lista de campos requeridos

    Returns:
        function: Decorador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener datos de la petición
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            # Verificar campos requeridos
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return jsonify({
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def validate_ip_address(ip_address):
    """
    Valida que una dirección IP sea válida

    Args:
        ip_address (str): Dirección IP

    Returns:
        bool: True si es válida
    """
    # Patrón para IPv4
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'

    if not re.match(ipv4_pattern, ip_address):
        return False

    # Verificar que cada octeto esté en el rango 0-255
    octets = ip_address.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def sanitize_input(text, max_length=1000):
    """
    Sanitiza entrada de texto para prevenir XSS

    Args:
        text (str): Texto a sanitizar
        max_length (int): Longitud máxima permitida

    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ''

    # Limitar longitud
    text = text[:max_length]

    # Eliminar caracteres de control
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    # Escapar caracteres HTML peligrosos
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }

    return "".join(html_escape_table.get(c, c) for c in text)


def validate_csrf_token(token, session_token):
    """
    Valida un token CSRF

    Args:
        token (str): Token recibido
        session_token (str): Token en sesión

    Returns:
        bool: True si el token es válido
    """
    if not token or not session_token:
        return False

    return token == session_token


def is_safe_redirect_url(target):
    """
    Verifica que una URL de redirección sea segura (previene open redirect)

    Args:
        target (str): URL objetivo

    Returns:
        bool: True si es segura
    """
    if not target:
        return False

    # No permitir URLs absolutas (solo relativas)
    if target.startswith('http://') or target.startswith('https://'):
        return False

    # No permitir caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '\\']
    if any(char in target for char in dangerous_chars):
        return False

    return True


def check_content_type(allowed_types):
    """
    Decorador para validar el Content-Type de la petición

    Args:
        allowed_types (list): Lista de tipos de contenido permitidos

    Returns:
        function: Decorador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.headers.get('Content-Type', '')

            # Verificar si el Content-Type está permitido
            if not any(allowed in content_type for allowed in allowed_types):
                return jsonify({
                    'error': f'Content-Type no permitido. Esperado: {", ".join(allowed_types)}'
                }), 415

            return f(*args, **kwargs)

        return decorated_function
    return decorator


class SecurityHeaders:
    """
    Clase para manejar headers de seguridad
    """

    @staticmethod
    def get_default_headers():
        """
        Obtiene los headers de seguridad por defecto

        Returns:
            dict: Headers de seguridad
        """
        return {
            # HSTS - HTTP Strict Transport Security
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',

            # Prevenir MIME sniffing
            'X-Content-Type-Options': 'nosniff',

            # Protección XSS
            'X-XSS-Protection': '1; mode=block',

            # Prevenir clickjacking
            'X-Frame-Options': 'SAMEORIGIN',

            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "connect-src 'self' https://api.stripe.com; "
                "frame-src https://js.stripe.com https://hooks.stripe.com;"
            ),

            # Referrer Policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',

            # Permissions Policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }

    @staticmethod
    def apply_to_response(response):
        """
        Aplica los headers de seguridad a una respuesta

        Args:
            response: Objeto de respuesta de Flask

        Returns:
            response: Respuesta con headers aplicados
        """
        headers = SecurityHeaders.get_default_headers()

        for header, value in headers.items():
            response.headers[header] = value

        return response


def init_security(app):
    """
    Inicializa configuraciones de seguridad en la aplicación

    Args:
        app: Instancia de Flask
    """

    @app.after_request
    def add_security_headers(response):
        """Aplica headers de seguridad a todas las respuestas"""
        return SecurityHeaders.apply_to_response(response)

    print("✅ Configuración de seguridad aplicada")


# Exportar utilidades
__all__ = [
    'validate_filename',
    'sanitize_filename',
    'validate_file_extension',
    'check_file_size',
    'validate_request_data',
    'validate_ip_address',
    'sanitize_input',
    'validate_csrf_token',
    'is_safe_redirect_url',
    'check_content_type',
    'SecurityHeaders',
    'init_security'
]
