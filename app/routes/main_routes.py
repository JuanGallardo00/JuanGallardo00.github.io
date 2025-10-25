"""
Rutas principales del CV y páginas generales
"""
from flask import Blueprint, render_template, jsonify

# Crear blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Página principal - CV profesional
    """
    # Datos del CV
    cv_data = {
        'nombre': 'Juan Antonio Gallardo Molina',
        'titulo': 'Ingeniero en Desarrollo de Software',
        'email': 'juan.gallardomolina@cesunbc.edu.mx',
        'telefono': '+6631154939',
        'linkedin': 'linkedin.com/in/juan-antonio-gallardo-molina-881738298',
        'github': 'github.com/JuanGallardo00',
        
        'sobre_mi': 'Ingeniero en Desarrollo de Software con experiencia en programación funcional, '
                   'desarrollo web con Flask y Python. Apasionado por crear soluciones innovadoras '
                   'y seguras.',
        
        'habilidades': [
            {'nombre': 'Python', 'nivel': 90},
            {'nombre': 'Flask', 'nivel': 85},
            {'nombre': 'JavaScript', 'nivel': 80},
            {'nombre': 'HTML/CSS', 'nivel': 85},
            {'nombre': 'Git', 'nivel': 80},
            {'nombre': 'SQL', 'nivel': 75},
        ],
        
        'experiencia': [
            {
                'puesto': 'Tecnico de SetUP',
                'empresa': 'Foxconn',
                'periodo': '2019 - 2022',
                'descripcion': 'Ejecución de setups en equipos SMT, asegurando transiciones eficientes entre modelos, correcta configuracion de programas y cumplimiento de especificaciones técnicas'
            },
            {
                'puesto': 'Tecnico en Mantenimiento Correctivo',
                'empresa': 'Foxconn',
                'periodo': '2023 - presente',
                'descripcion': 'Atención inmediata a paros de línea, análisis de causas raíz y aplicación de soluciones correctivas en equipos electrónicos y de automatización.'
            }
        ],
        
        'educacion': [
            {
                'titulo': 'Ingeniería en Desarrollo de Software',
                'institucion': 'CESUN Universidad',
                'periodo': '2023 - 2026'
            }
        ],
        
        'proyectos': [
            {
                'nombre': 'CV + DocConvert',
                'descripcion': 'Aplicación web para mostrar CV y convertir documentos PDF con integración de pagos Stripe.',
                'tecnologias': ['Flask', 'Python', 'Stripe', 'PyPDF2']
            }
        ]
    }
    
    return render_template('index.html', cv=cv_data)


@main_bp.route('/contacto')
def contacto():
    """
    Página de contacto
    """
    return render_template('contacto.html')


@main_bp.route('/api/health')
def health_check():
    """
    Endpoint de verificación de salud de la API
    """
    return jsonify({
        'status': 'ok',
        'message': 'CV-DocConvert API is running',
        'version': '1.0.0'
    }), 200
