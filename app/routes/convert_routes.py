"""
Rutas del convertidor de documentos
"""
from flask import Blueprint, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from app.services.converters import DocumentConverter
from app.services.cleanup import init_cleanup_service
import os
from datetime import datetime

# Crear blueprint
convert_bp = Blueprint('convert', __name__)

# Inicializar convertidor y servicio de limpieza
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
converter = DocumentConverter(UPLOAD_FOLDER)
cleanup_service = init_cleanup_service(UPLOAD_FOLDER, max_age_minutes=30, interval_minutes=10)


@convert_bp.route('/')
def convert_page():
    """
    Página del convertidor de documentos
    """
    return render_template('convert.html')


@convert_bp.route('/upload/images-to-pdf', methods=['POST'])
def upload_images_to_pdf():
    """
    Convierte imágenes a PDF
    """
    try:
        # Debug: imprimir lo que se recibió
        print(f"Request files keys: {list(request.files.keys())}")
        print(f"Request form keys: {list(request.form.keys())}")

        # Verificar que se enviaron archivos
        if 'files[]' not in request.files:
            return jsonify({'error': 'No se enviaron archivos. Recibido: ' + str(list(request.files.keys()))}), 400

        files = request.files.getlist('files[]')

        if not files or files[0].filename == '':
            return jsonify({'error': 'No se seleccionaron archivos'}), 400

        # Guardar y validar archivos
        image_paths = []
        for file in files:
            if not converter.allowed_file(file.filename, 'image'):
                return jsonify({'error': f'Formato no permitido: {file.filename}'}), 400

            filepath = converter.save_file(file)
            image_paths.append(filepath)

        # Convertir a PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'converted_{timestamp}.pdf'
        pdf_path = converter.images_to_pdf(image_paths, output_filename)

        # Limpiar imágenes temporales
        for img_path in image_paths:
            converter.delete_file(img_path)

        return jsonify({
            'success': True,
            'message': 'Imágenes convertidas a PDF exitosamente',
            'filename': output_filename,
            'download_url': f'/convert/download/{output_filename}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al convertir: {str(e)}'}), 500


@convert_bp.route('/upload/merge-pdfs', methods=['POST'])
def upload_merge_pdfs():
    """
    Une múltiples PDFs en uno solo
    """
    try:
        # Verificar que se enviaron archivos
        if 'files[]' not in request.files:
            return jsonify({'error': 'No se enviaron archivos'}), 400

        files = request.files.getlist('files[]')

        if not files or files[0].filename == '':
            return jsonify({'error': 'No se seleccionaron archivos'}), 400

        # Guardar y validar archivos
        pdf_paths = []
        for file in files:
            if not converter.allowed_file(file.filename, 'pdf'):
                return jsonify({'error': f'Solo se permiten archivos PDF: {file.filename}'}), 400

            filepath = converter.save_file(file)
            pdf_paths.append(filepath)

        # Unir PDFs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'merged_{timestamp}.pdf'
        merged_path = converter.merge_pdfs(pdf_paths, output_filename)

        # Limpiar PDFs temporales
        for pdf_path in pdf_paths:
            converter.delete_file(pdf_path)

        return jsonify({
            'success': True,
            'message': 'PDFs unidos exitosamente',
            'filename': output_filename,
            'download_url': f'/convert/download/{output_filename}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al unir PDFs: {str(e)}'}), 500


@convert_bp.route('/upload/split-pdf', methods=['POST'])
def upload_split_pdf():
    """
    Divide un PDF o extrae páginas específicas
    """
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        if not converter.allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

        # Guardar archivo
        filepath = converter.save_file(file)

        # Obtener parámetros de páginas
        start_page = request.form.get('start_page', type=int)
        end_page = request.form.get('end_page', type=int)

        # Dividir PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'split_{timestamp}.pdf'
        split_path = converter.split_pdf(filepath, start_page, end_page, output_filename)

        # Limpiar PDF temporal
        converter.delete_file(filepath)

        return jsonify({
            'success': True,
            'message': 'PDF dividido exitosamente',
            'filename': output_filename,
            'download_url': f'/convert/download/{output_filename}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al dividir PDF: {str(e)}'}), 500


@convert_bp.route('/pdf-info', methods=['POST'])
def get_pdf_info():
    """
    Obtiene información de un PDF
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        if not converter.allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

        # Guardar archivo temporalmente
        filepath = converter.save_file(file)

        # Obtener información
        info = converter.get_pdf_info(filepath)

        # Limpiar archivo temporal
        converter.delete_file(filepath)

        return jsonify({
            'success': True,
            'info': info
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al obtener información: {str(e)}'}), 500


@convert_bp.route('/download/<filename>')
def download_file(filename):
    """
    Descarga un archivo convertido
    """
    try:
        # Validar nombre de archivo (seguridad)
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': f'Error al descargar: {str(e)}'}), 500


@convert_bp.route('/stats')
def get_stats():
    """
    Obtiene estadísticas de la carpeta de uploads
    """
    stats = cleanup_service.get_folder_stats()
    return jsonify(stats), 200
