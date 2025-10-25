# CV + DocConvert

Aplicación Flask que muestra un CV profesional y ofrece un convertidor de documentos.  
Incluye integración con Stripe para recibir donaciones voluntarias.

## Instalación
```bash
pip install -r requirements.txt
```

## Configuración
Crear archivo `.env` con:
```
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
WEBHOOK_SECRET=whsec_xxx
SECRET_KEY=secret
```

## Seguridad Implementada
- Claves API en variables de entorno (.env).
- Protección XSS y CORS limitado.
- Webhook Stripe verificado por firma.
- HTTPS obligatorio en despliegue.
- Rate limiting en rutas sensibles.

## Ejecución
```bash
python run.py
```