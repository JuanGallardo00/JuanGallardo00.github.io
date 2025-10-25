/**
 * Validaciones frontend para CV-DocConvert
 * Incluye validación de archivos, tamaños, tipos y seguridad
 */

// Configuración de validación
const VALIDATION_CONFIG = {
    // Tamaños de archivo
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16 MB
    MAX_TOTAL_SIZE: 50 * 1024 * 1024, // 50 MB total

    // Tipos de archivo permitidos
    ALLOWED_IMAGE_TYPES: ['image/png', 'image/jpeg', 'image/jpg'],
    ALLOWED_PDF_TYPE: 'application/pdf',

    // Extensiones permitidas
    ALLOWED_IMAGE_EXTENSIONS: ['.png', '.jpg', '.jpeg'],
    ALLOWED_PDF_EXTENSION: '.pdf',

    // Límites
    MAX_FILES: 20,
    MIN_FILES: 1
};

/**
 * Valida el tamaño de un archivo
 * @param {File} file - Archivo a validar
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateFileSize(file) {
    if (file.size > VALIDATION_CONFIG.MAX_FILE_SIZE) {
        const maxSizeMB = (VALIDATION_CONFIG.MAX_FILE_SIZE / (1024 * 1024)).toFixed(2);
        return {
            valid: false,
            error: `El archivo "${file.name}" excede el tamaño máximo de ${maxSizeMB} MB`
        };
    }

    if (file.size === 0) {
        return {
            valid: false,
            error: `El archivo "${file.name}" está vacío`
        };
    }

    return { valid: true };
}

/**
 * Valida el tipo de archivo (imagen)
 * @param {File} file - Archivo a validar
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateImageFile(file) {
    // Validar tipo MIME
    if (!VALIDATION_CONFIG.ALLOWED_IMAGE_TYPES.includes(file.type)) {
        return {
            valid: false,
            error: `El archivo "${file.name}" no es una imagen válida (PNG, JPG, JPEG)`
        };
    }

    // Validar extensión
    const extension = getFileExtension(file.name);
    if (!VALIDATION_CONFIG.ALLOWED_IMAGE_EXTENSIONS.includes(extension)) {
        return {
            valid: false,
            error: `La extensión del archivo "${file.name}" no es válida`
        };
    }

    return { valid: true };
}

/**
 * Valida el tipo de archivo (PDF)
 * @param {File} file - Archivo a validar
 * @returns {Object} - {valid: boolean, error: string}
 */
function validatePdfFile(file) {
    // Validar tipo MIME
    if (file.type !== VALIDATION_CONFIG.ALLOWED_PDF_TYPE) {
        return {
            valid: false,
            error: `El archivo "${file.name}" no es un PDF válido`
        };
    }

    // Validar extensión
    const extension = getFileExtension(file.name);
    if (extension !== VALIDATION_CONFIG.ALLOWED_PDF_EXTENSION) {
        return {
            valid: false,
            error: `La extensión del archivo "${file.name}" debe ser .pdf`
        };
    }

    return { valid: true };
}

/**
 * Valida múltiples archivos de imagen
 * @param {FileList} files - Lista de archivos
 * @returns {Object} - {valid: boolean, error: string, files: Array}
 */
function validateImageFiles(files) {
    // Validar cantidad de archivos
    if (files.length < VALIDATION_CONFIG.MIN_FILES) {
        return {
            valid: false,
            error: 'Debe seleccionar al menos un archivo'
        };
    }

    if (files.length > VALIDATION_CONFIG.MAX_FILES) {
        return {
            valid: false,
            error: `No puede seleccionar más de ${VALIDATION_CONFIG.MAX_FILES} archivos`
        };
    }

    // Validar cada archivo
    let totalSize = 0;
    const validFiles = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Validar tamaño
        const sizeValidation = validateFileSize(file);
        if (!sizeValidation.valid) {
            return sizeValidation;
        }

        // Validar tipo
        const typeValidation = validateImageFile(file);
        if (!typeValidation.valid) {
            return typeValidation;
        }

        totalSize += file.size;
        validFiles.push(file);
    }

    // Validar tamaño total
    if (totalSize > VALIDATION_CONFIG.MAX_TOTAL_SIZE) {
        const maxTotalMB = (VALIDATION_CONFIG.MAX_TOTAL_SIZE / (1024 * 1024)).toFixed(2);
        return {
            valid: false,
            error: `El tamaño total de los archivos excede ${maxTotalMB} MB`
        };
    }

    return {
        valid: true,
        files: validFiles,
        totalSize: totalSize
    };
}

/**
 * Valida múltiples archivos PDF
 * @param {FileList} files - Lista de archivos
 * @returns {Object} - {valid: boolean, error: string, files: Array}
 */
function validatePdfFiles(files) {
    // Validar cantidad de archivos
    if (files.length < VALIDATION_CONFIG.MIN_FILES) {
        return {
            valid: false,
            error: 'Debe seleccionar al menos un archivo PDF'
        };
    }

    if (files.length > VALIDATION_CONFIG.MAX_FILES) {
        return {
            valid: false,
            error: `No puede seleccionar más de ${VALIDATION_CONFIG.MAX_FILES} archivos`
        };
    }

    // Validar cada archivo
    let totalSize = 0;
    const validFiles = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Validar tamaño
        const sizeValidation = validateFileSize(file);
        if (!sizeValidation.valid) {
            return sizeValidation;
        }

        // Validar tipo
        const typeValidation = validatePdfFile(file);
        if (!typeValidation.valid) {
            return typeValidation;
        }

        totalSize += file.size;
        validFiles.push(file);
    }

    // Validar tamaño total
    if (totalSize > VALIDATION_CONFIG.MAX_TOTAL_SIZE) {
        const maxTotalMB = (VALIDATION_CONFIG.MAX_TOTAL_SIZE / (1024 * 1024)).toFixed(2);
        return {
            valid: false,
            error: `El tamaño total de los archivos excede ${maxTotalMB} MB`
        };
    }

    return {
        valid: true,
        files: validFiles,
        totalSize: totalSize
    };
}

/**
 * Sanitiza el nombre de un archivo
 * @param {string} filename - Nombre del archivo
 * @returns {string} - Nombre sanitizado
 */
function sanitizeFilename(filename) {
    // Eliminar caracteres peligrosos
    return filename.replace(/[^a-zA-Z0-9._-]/g, '_');
}

/**
 * Obtiene la extensión de un archivo
 * @param {string} filename - Nombre del archivo
 * @returns {string} - Extensión en minúsculas
 */
function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
}

/**
 * Formatea el tamaño de un archivo
 * @param {number} bytes - Tamaño en bytes
 * @returns {string} - Tamaño formateado
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Valida un monto de donación
 * @param {number} amount - Monto en centavos
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateDonationAmount(amount) {
    // Convertir a número
    const amountNum = Number(amount);

    if (isNaN(amountNum)) {
        return {
            valid: false,
            error: 'El monto debe ser un número válido'
        };
    }

    if (amountNum < 50) {
        return {
            valid: false,
            error: 'El monto mínimo es $0.50'
        };
    }

    if (amountNum > 99999999) {
        return {
            valid: false,
            error: 'El monto máximo es $999,999.99'
        };
    }

    return { valid: true };
}

/**
 * Sanitiza entrada de texto para prevenir XSS
 * @param {string} text - Texto a sanitizar
 * @returns {string} - Texto sanitizado
 */
function sanitizeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Valida un email
 * @param {string} email - Email a validar
 * @returns {boolean} - True si es válido
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Previene la inyección de código en inputs
 * @param {HTMLInputElement} input - Input a proteger
 */
function preventCodeInjection(input) {
    input.addEventListener('input', function(e) {
        // Detectar patrones peligrosos
        const dangerousPatterns = [
            /<script/i,
            /javascript:/i,
            /onerror=/i,
            /onclick=/i,
            /onload=/i
        ];

        for (let pattern of dangerousPatterns) {
            if (pattern.test(this.value)) {
                this.value = this.value.replace(pattern, '');
                console.warn('Intento de inyección de código detectado y bloqueado');
            }
        }
    });
}

/**
 * Configura la validación en tiempo real para un input de archivo
 * @param {string} inputId - ID del input
 * @param {string} type - Tipo de validación ('image' o 'pdf')
 * @param {Function} callback - Función callback después de validar
 */
function setupFileInputValidation(inputId, type, callback) {
    const input = document.getElementById(inputId);

    if (!input) {
        console.error(`Input con ID "${inputId}" no encontrado`);
        return;
    }

    input.addEventListener('change', function(e) {
        const files = e.target.files;

        if (files.length === 0) {
            return;
        }

        let validation;

        if (type === 'image') {
            validation = validateImageFiles(files);
        } else if (type === 'pdf') {
            validation = validatePdfFiles(files);
        } else {
            console.error('Tipo de validación no válido');
            return;
        }

        if (callback) {
            callback(validation);
        }
    });
}

// Exportar funciones para uso global
if (typeof window !== 'undefined') {
    window.FileValidator = {
        validateFileSize,
        validateImageFile,
        validatePdfFile,
        validateImageFiles,
        validatePdfFiles,
        sanitizeFilename,
        getFileExtension,
        formatFileSize,
        validateDonationAmount,
        sanitizeText,
        validateEmail,
        preventCodeInjection,
        setupFileInputValidation,
        CONFIG: VALIDATION_CONFIG
    };
}

console.log(' Validaciones frontend cargadas correctamente');
