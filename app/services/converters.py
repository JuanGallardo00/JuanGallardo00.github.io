"""
Servicio de conversión de documentos
Funciones para convertir imágenes a PDF, unir PDFs, dividir PDFs, etc.
"""
import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from werkzeug.utils import secure_filename
from datetime import datetime


class DocumentConverter:
    """Clase para manejar conversiones de documentos"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
    
    def __init__(self, upload_folder):
        """
        Inicializa el convertidor
        
        Args:
            upload_folder (str): Carpeta donde se guardarán los archivos
        """
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename, file_type='image'):
        """
        Verifica si el archivo tiene una extensión permitida
        
        Args:
            filename (str): Nombre del archivo
            file_type (str): Tipo de archivo ('image' o 'pdf')
        
        Returns:
            bool: True si la extensión es permitida
        """
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'image':
            return ext in self.ALLOWED_IMAGE_EXTENSIONS
        elif file_type == 'pdf':
            return ext in self.ALLOWED_PDF_EXTENSIONS
        else:
            return ext in (self.ALLOWED_IMAGE_EXTENSIONS | self.ALLOWED_PDF_EXTENSIONS)
    
    def save_file(self, file):
        """
        Guarda un archivo de forma segura
        
        Args:
            file: Archivo de Flask
        
        Returns:
            str: Ruta del archivo guardado
        """
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath
    
    def images_to_pdf(self, image_paths, output_filename='converted.pdf'):
        """
        Convierte múltiples imágenes a un único PDF
        
        Args:
            image_paths (list): Lista de rutas de imágenes
            output_filename (str): Nombre del archivo PDF de salida
        
        Returns:
            str: Ruta del PDF generado
        """
        if not image_paths:
            raise ValueError("No se proporcionaron imágenes para convertir")
        
        # Convertir imágenes a RGB si es necesario
        images = []
        for img_path in image_paths:
            img = Image.open(img_path)
            # Convertir a RGB si es RGBA o escala de grises
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                images.append(rgb_img)
            elif img.mode != 'RGB':
                images.append(img.convert('RGB'))
            else:
                images.append(img)
        
        # Guardar como PDF
        output_path = os.path.join(self.upload_folder, output_filename)
        
        if len(images) == 1:
            images[0].save(output_path, 'PDF', resolution=100.0)
        else:
            images[0].save(
                output_path, 
                'PDF', 
                resolution=100.0, 
                save_all=True, 
                append_images=images[1:]
            )
        
        return output_path
    
    def merge_pdfs(self, pdf_paths, output_filename='merged.pdf'):
        """
        Une múltiples PDFs en uno solo
        
        Args:
            pdf_paths (list): Lista de rutas de PDFs
            output_filename (str): Nombre del archivo PDF de salida
        
        Returns:
            str: Ruta del PDF unido
        """
        if not pdf_paths:
            raise ValueError("No se proporcionaron PDFs para unir")
        
        merger = PdfMerger()
        
        for pdf_path in pdf_paths:
            merger.append(pdf_path)
        
        output_path = os.path.join(self.upload_folder, output_filename)
        merger.write(output_path)
        merger.close()
        
        return output_path
    
    def split_pdf(self, pdf_path, start_page=None, end_page=None, output_filename='split.pdf'):
        """
        Divide un PDF o extrae páginas específicas
        
        Args:
            pdf_path (str): Ruta del PDF original
            start_page (int): Página inicial (1-indexed)
            end_page (int): Página final (1-indexed)
            output_filename (str): Nombre del archivo PDF de salida
        
        Returns:
            str: Ruta del PDF dividido
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Si no se especifican páginas, extraer todas
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = total_pages
        
        # Validar rangos
        start_page = max(1, min(start_page, total_pages))
        end_page = max(start_page, min(end_page, total_pages))
        
        # Agregar páginas (convertir a 0-indexed)
        for page_num in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page_num])
        
        output_path = os.path.join(self.upload_folder, output_filename)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def get_pdf_info(self, pdf_path):
        """
        Obtiene información sobre un PDF
        
        Args:
            pdf_path (str): Ruta del PDF
        
        Returns:
            dict: Información del PDF
        """
        reader = PdfReader(pdf_path)
        
        info = {
            'pages': len(reader.pages),
            'metadata': reader.metadata if reader.metadata else {},
            'size_bytes': os.path.getsize(pdf_path),
            'size_mb': round(os.path.getsize(pdf_path) / (1024 * 1024), 2)
        }
        
        return info
    
    def delete_file(self, filepath):
        """
        Elimina un archivo
        
        Args:
            filepath (str): Ruta del archivo a eliminar
        """
        if os.path.exists(filepath):
            os.remove(filepath)
