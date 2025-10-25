"""
Rutas de integración con Stripe para donaciones
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import stripe
import os
from config.stripe_config import get_stripe_public_key, get_webhook_secret

# Crear blueprint
stripe_bp = Blueprint('stripe', __name__)


@stripe_bp.route('/donate')
def donate_page():
    """
    Página de donaciones
    """
    # Obtener clave pública de Stripe para el frontend
    stripe_public_key = get_stripe_public_key()

    return render_template('donate.html', stripe_public_key=stripe_public_key)


@stripe_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Crea una sesión de checkout de Stripe
    """
    try:
        # Obtener el monto de la donación desde el formulario
        data = request.get_json()
        amount = data.get('amount', 500)  # Monto en centavos (500 = $5.00)

        # Validar monto mínimo (50 centavos = $0.50)
        if amount < 50:
            return jsonify({'error': 'El monto mínimo es $0.50'}), 400

        # Validar monto máximo ($999,999.99)
        if amount > 99999999:
            return jsonify({'error': 'El monto máximo es $999,999.99'}), 400

        # Crear sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount,
                        'product_data': {
                            'name': 'Donación a CV-DocConvert',
                            'description': 'Gracias por apoyar este proyecto',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'stripe/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'stripe/donate',
        )

        return jsonify({
            'id': checkout_session.id,
            'url': checkout_session.url
        }), 200

    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error al crear sesión: {str(e)}'}), 500


@stripe_bp.route('/success')
def success_page():
    """
    Página de éxito después de una donación
    """
    session_id = request.args.get('session_id')

    if not session_id:
        return redirect(url_for('stripe.donate_page'))

    try:
        # Recuperar la sesión de checkout
        session = stripe.checkout.Session.retrieve(session_id)

        # Obtener detalles de la donación
        amount_total = session.get('amount_total', 0) / 100  # Convertir de centavos a dólares

        return render_template('thanks.html',
                             amount=amount_total,
                             session_id=session_id)

    except stripe.error.StripeError as e:
        return render_template('thanks.html',
                             error=f'Error al verificar la donación: {str(e)}')


@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook de Stripe para procesar eventos
    Verifica la firma del webhook para seguridad
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = get_webhook_secret()

    if not webhook_secret:
        return jsonify({'error': 'Webhook secret no configurado'}), 500

    try:
        # Verificar y construir el evento
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Payload inválido
        return jsonify({'error': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida
        return jsonify({'error': 'Firma inválida'}), 400

    # Procesar el evento
    event_type = event['type']

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)

    elif event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)

    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failed(payment_intent)

    # Otros eventos pueden ser manejados aquí

    return jsonify({'status': 'success'}), 200


def handle_checkout_session_completed(session):
    """
    Maneja el evento cuando se completa una sesión de checkout

    Args:
        session: Objeto de sesión de Stripe
    """
    # Aquí puedes:
    # - Guardar la donación en una base de datos
    # - Enviar un email de agradecimiento
    # - Registrar logs

    session_id = session.get('id')
    customer_email = session.get('customer_details', {}).get('email')
    amount_total = session.get('amount_total', 0) / 100

    print(f"✅ Donación completada:")
    print(f"   Session ID: {session_id}")
    print(f"   Email: {customer_email}")
    print(f"   Monto: ${amount_total:.2f}")


def handle_payment_intent_succeeded(payment_intent):
    """
    Maneja el evento cuando un pago es exitoso

    Args:
        payment_intent: Objeto de payment intent de Stripe
    """
    payment_id = payment_intent.get('id')
    amount = payment_intent.get('amount', 0) / 100

    print(f"✅ Pago exitoso:")
    print(f"   Payment ID: {payment_id}")
    print(f"   Monto: ${amount:.2f}")


def handle_payment_failed(payment_intent):
    """
    Maneja el evento cuando un pago falla

    Args:
        payment_intent: Objeto de payment intent de Stripe
    """
    payment_id = payment_intent.get('id')
    error_message = payment_intent.get('last_payment_error', {}).get('message', 'Error desconocido')

    print(f"❌ Pago fallido:")
    print(f"   Payment ID: {payment_id}")
    print(f"   Error: {error_message}")


@stripe_bp.route('/config')
def get_config():
    """
    Endpoint para obtener la clave pública de Stripe
    """
    return jsonify({
        'publicKey': get_stripe_public_key()
    }), 200
