"""
Servicio de limpieza automática de archivos temporales
"""
import os
import time
import threading
from datetime import datetime


class FileCleanupService:
    """Servicio para limpiar archivos temporales automáticamente"""
    
    def __init__(self, folder_path, max_age_minutes=30):
        """
        Inicializa el servicio de limpieza
        
        Args:
            folder_path (str): Carpeta a limpiar
            max_age_minutes (int): Tiempo máximo de vida de los archivos en minutos
        """
        self.folder_path = folder_path
        self.max_age_seconds = max_age_minutes * 60
        self.running = False
        self.thread = None
    
    def cleanup_old_files(self):
        """
        Elimina archivos más antiguos que max_age_seconds
        
        Returns:
            int: Número de archivos eliminados
        """
        if not os.path.exists(self.folder_path):
            return 0
        
        deleted_count = 0
        current_time = time.time()
        
        try:
            for filename in os.listdir(self.folder_path):
                filepath = os.path.join(self.folder_path, filename)
                
                # Solo procesar archivos (no directorios)
                if not os.path.isfile(filepath):
                    continue
                
                # Obtener tiempo de modificación del archivo
                file_age = current_time - os.path.getmtime(filepath)
                
                # Si el archivo es más viejo que max_age_seconds, eliminarlo
                if file_age > self.max_age_seconds:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"Archivo eliminado: {filename} (edad: {int(file_age/60)} minutos)")
                    except Exception as e:
                        print(f"Error al eliminar {filename}: {str(e)}")

        except Exception as e:
            print(f"Error durante limpieza: {str(e)}")

        if deleted_count > 0:
            print(f"Limpieza completada: {deleted_count} archivo(s) eliminado(s)")
        
        return deleted_count
    
    def start_auto_cleanup(self, interval_minutes=10):
        """
        Inicia la limpieza automática en un hilo separado
        
        Args:
            interval_minutes (int): Intervalo entre limpiezas en minutos
        """
        if self.running:
            print("El servicio de limpieza ya esta ejecutandose")
            return

        self.running = True
        interval_seconds = interval_minutes * 60

        def cleanup_loop():
            """Loop de limpieza que se ejecuta periódicamente"""
            print(f"Servicio de limpieza iniciado (cada {interval_minutes} minutos)")

            while self.running:
                try:
                    # Ejecutar limpieza
                    self.cleanup_old_files()

                    # Esperar antes de la siguiente limpieza
                    time.sleep(interval_seconds)

                except Exception as e:
                    print(f"Error en loop de limpieza: {str(e)}")
                    time.sleep(60)  # Esperar 1 minuto antes de reintentar
        
        # Crear y iniciar hilo
        self.thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.thread.start()
    
    def stop_auto_cleanup(self):
        """Detiene la limpieza automática"""
        if not self.running:
            print("El servicio de limpieza no esta ejecutandose")
            return

        self.running = False
        print("Servicio de limpieza detenido")
    
    def get_folder_stats(self):
        """
        Obtiene estadísticas de la carpeta
        
        Returns:
            dict: Estadísticas de la carpeta
        """
        if not os.path.exists(self.folder_path):
            return {
                'exists': False,
                'file_count': 0,
                'total_size_mb': 0
            }
        
        file_count = 0
        total_size = 0
        
        for filename in os.listdir(self.folder_path):
            filepath = os.path.join(self.folder_path, filename)
            if os.path.isfile(filepath):
                file_count += 1
                total_size += os.path.getsize(filepath)
        
        return {
            'exists': True,
            'file_count': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'folder_path': self.folder_path
        }


def init_cleanup_service(upload_folder, max_age_minutes=30, interval_minutes=10):
    """
    Inicializa y arranca el servicio de limpieza
    
    Args:
        upload_folder (str): Carpeta a limpiar
        max_age_minutes (int): Tiempo máximo de vida de los archivos
        interval_minutes (int): Intervalo entre limpiezas
    
    Returns:
        FileCleanupService: Instancia del servicio
    """
    cleanup_service = FileCleanupService(upload_folder, max_age_minutes)
    cleanup_service.start_auto_cleanup(interval_minutes)
    return cleanup_service
