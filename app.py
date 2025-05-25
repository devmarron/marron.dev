# app.py - Flask Backend para marron.dev Contact Form (CORS FIXED)
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from datetime import datetime
import re
from typing import Dict, Any
import logging

# Cargar variables de entorno
load_dotenv()

# Debug: Verificar variables de entorno
print("🔧 DEBUG - Variables de entorno:")
print(f"MAIL_USERNAME: {os.environ.get('MAIL_USERNAME', 'NO ENCONTRADO')}")
print(
    f"MAIL_PASSWORD: {'*' * len(os.environ.get('MAIL_PASSWORD', '')) if os.environ.get('MAIL_PASSWORD') else 'NO ENCONTRADO'}")
print(f"ADMIN_EMAIL: {os.environ.get('ADMIN_EMAIL', 'NO ENCONTRADO')}")
print("=" * 50)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ✅ CORS CONFIGURACIÓN CORREGIDA
CORS(app,
     origins=["http://localhost:3000", "http://127.0.0.1:5000", "http://localhost:5000", "file://", "*"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Accept", "Authorization"],
     supports_credentials=True
     )

# Rate limiting para evitar spam
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Configuración de email (usando Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('marron.dev', os.environ.get('MAIL_USERNAME'))

# Inicializar extensiones
mail = Mail(app)

# Configuración
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
PROJECT_TYPES = {
    'ui-ux-design': 'UI/UX Design',
    'web-development': 'Web Development',
    'mobile-solutions': 'Mobile Solutions',
    'brand-identity': 'Brand Identity',
    'digital-strategy': 'Digital Strategy',
    'product-launch': 'Product Launch',
    'other': 'Other'
}

BUDGET_RANGES = {
    '5k-15k': '$5K - $15K',
    '15k-30k': '$15K - $30K',
    '30k-50k': '$30K - $50K',
    '50k-100k': '$50K - $100K',
    '100k+': '$100K+'
}


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(text: str) -> str:
    """Limpiar input del usuario"""
    if not text:
        return ''
    return text.strip()[:1000]


def validate_contact_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validar datos del formulario de contacto"""
    errors = {}

    # Campos requeridos
    required_fields = ['firstName', 'lastName', 'email', 'projectType', 'message']
    for field in required_fields:
        if not data.get(field, '').strip():
            errors[field] = f'{field} is required'

    # Validar email
    if data.get('email') and not validate_email(data['email']):
        errors['email'] = 'Invalid email format'

    # Validar project type
    if data.get('projectType') and data['projectType'] not in PROJECT_TYPES:
        errors['projectType'] = 'Invalid project type'

    # Validar budget (opcional)
    if data.get('budget') and data['budget'] not in BUDGET_RANGES:
        errors['budget'] = 'Invalid budget range'

    return errors


def create_email_template(data: Dict[str, Any]) -> str:
    """Crear template del email para admin"""
    project_type = PROJECT_TYPES.get(data.get('projectType', ''), 'Not specified')
    budget = BUDGET_RANGES.get(data.get('budget', ''), 'Not specified')
    
    # Corrección: Mover el replace fuera del f-string
    message_formatted = data['message'].replace('\n', '<br>')

    template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1A1A1A; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #FF6B35 0%, #7B4A2A 100%); 
                       color: white; padding: 30px 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #FAFAFA; padding: 30px 20px; }}
            .field {{ margin-bottom: 20px; }}
            .field-label {{ font-weight: 600; color: #7B4A2A; margin-bottom: 5px; }}
            .field-value {{ background: white; padding: 15px; border-radius: 4px; border-left: 3px solid #FF6B35; }}
            .footer {{ background: #1A1A1A; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 8px 8px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 New Contact Form Submission</h1>
                <p>marron.dev</p>
            </div>

            <div class="content">
                <div class="field">
                    <div class="field-label">👤 Contact Information</div>
                    <div class="field-value">
                        <strong>Name:</strong> {data['firstName']} {data['lastName']}<br>
                        <strong>Email:</strong> <a href="mailto:{data['email']}">{data['email']}</a><br>
                        <strong>Company:</strong> {data.get('company', 'Not provided')}
                    </div>
                </div>

                <div class="field">
                    <div class="field-label">💼 Project Details</div>
                    <div class="field-value">
                        <strong>Project Type:</strong> {project_type}<br>
                        <strong>Budget Range:</strong> {budget}
                    </div>
                </div>

                <div class="field">
                    <div class="field-label">💬 Message</div>
                    <div class="field-value">
                        {message_formatted}
                    </div>
                </div>

                <div class="field">
                    <div class="field-label">⏰ Submission Time</div>
                    <div class="field-value">
                        {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>This email was sent from the marron.dev contact form</p>
                <p><strong>Respond within 24 hours for best client experience</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    return template


def create_client_confirmation_email(data: Dict[str, Any]) -> str:
    """Crear email de confirmación para el cliente"""
    template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1A1A1A; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #FF6B35 0%, #7B4A2A 100%); 
                       color: white; padding: 30px 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #FAFAFA; padding: 30px 20px; }}
            .footer {{ background: #1A1A1A; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 8px 8px; font-size: 14px; }}
            .cta {{ background: #FF6B35; color: white; padding: 15px 30px; 
                   text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Thank You for Reaching Out!</h1>
                <p>marron.dev</p>
            </div>

            <div class="content">
                <p>Hi {data['firstName']},</p>

                <p>Thank you for contacting marron.dev! We've received your message about your <strong>{PROJECT_TYPES.get(data.get('projectType', ''), 'project')}</strong> and we're excited to learn more.</p>

                <p><strong>What happens next?</strong></p>
                <ul>
                    <li>✅ Our team will review your project details</li>
                    <li>📞 We'll schedule a discovery call within 24 hours</li>
                    <li>💡 We'll prepare initial ideas and recommendations</li>
                    <li>🚀 Together, we'll plan your project roadmap</li>
                </ul>

                <p>In the meantime, feel free to check out our recent work and case studies:</p>
                <a href="https://marron.dev" class="cta">View Our Portfolio</a>

                <p>If you have any urgent questions, don't hesitate to reach out directly at <strong>hello@marron.dev</strong> or call us at <strong>+1 (555) 123-4567</strong>.</p>

                <p>Looking forward to creating something amazing together!</p>

                <p>Best regards,<br>
                <strong>The marron.dev Team</strong></p>
            </div>

            <div class="footer">
                <p>marron.dev - Digital Innovation Studio</p>
                <p>San Francisco, CA | hello@marron.dev</p>
            </div>
        </div>
    </body>
    </html>
    """
    return template


# ✅ ENDPOINT PRINCIPAL - CONTACT FORM
@app.route('/api/contact', methods=['POST', 'OPTIONS'])
@limiter.limit("5 per minute")
def handle_contact():
    """Manejar submissions del formulario de contacto"""

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        print("📋 OPTIONS request received (CORS preflight)")
        return '', 200

    print("📮 POST request received!")
    print(f"📋 Request headers: {dict(request.headers)}")
    print(f"📋 Request content type: {request.content_type}")

    try:
        # Obtener datos JSON
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        print(f"📋 Received data: {data}")

        if not data:
            print("❌ No data provided")
            return jsonify({'error': 'No data provided'}), 400

        # Sanitizar inputs
        sanitized_data = {
            'firstName': sanitize_input(data.get('firstName', '')),
            'lastName': sanitize_input(data.get('lastName', '')),
            'email': sanitize_input(data.get('email', '')),
            'company': sanitize_input(data.get('company', '')),
            'projectType': data.get('projectType', ''),
            'budget': data.get('budget', ''),
            'message': sanitize_input(data.get('message', ''))
        }

        print(f"📋 Sanitized data: {sanitized_data}")

        # Validar datos
        errors = validate_contact_data(sanitized_data)
        if errors:
            print(f"❌ Validation errors: {errors}")
            return jsonify({'errors': errors}), 400

        # Crear y enviar email al admin
        print("📧 Creating admin email...")
        admin_subject = f"🚀 New Contact: {sanitized_data['firstName']} {sanitized_data['lastName']} - {PROJECT_TYPES.get(sanitized_data['projectType'], 'General Inquiry')}"
        admin_body = create_email_template(sanitized_data)

        admin_msg = Message(
            subject=admin_subject,
            recipients=[ADMIN_EMAIL],
            html=admin_body,
            reply_to=sanitized_data['email']
        )

        # Crear email de confirmación al cliente
        print("📧 Creating client confirmation email...")
        client_subject = "Thank you for contacting marron.dev! 🎉"
        client_body = create_client_confirmation_email(sanitized_data)

        client_msg = Message(
            subject=client_subject,
            recipients=[sanitized_data['email']],
            html=client_body
        )

        # Enviar ambos emails
        print("📧 Sending admin email...")
        mail.send(admin_msg)
        print("✅ Admin email sent!")

        print("📧 Sending client confirmation email...")
        mail.send(client_msg)
        print("✅ Client confirmation email sent!")

        # Log successful submission
        logger.info(f"Contact form submitted successfully by {sanitized_data['email']}")
        print(f"✅ Form submission complete for {sanitized_data['email']}")

        return jsonify({
            'success': True,
            'message': 'Thank you! We\'ll get back to you within 24 hours.'
        }), 200

    except Exception as e:
        print(f"❌ ERROR in handle_contact: {str(e)}")
        logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'details': str(e) if app.debug else None
        }), 500


# ✅ ENDPOINT DE PRUEBA
@app.route('/api/test-email', methods=['GET', 'POST'])
def test_email():
    """Endpoint para probar la configuración de email"""
    try:
        print("🧪 Testing email configuration...")
        
        # Corrección: Mover la formación de fecha fuera del string
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        msg = Message(
            subject="🧪 Test Email - marron.dev Backend",
            recipients=[ADMIN_EMAIL],
            html=f"""
            <h1>✅ Email Configuration Test</h1>
            <p>If you're reading this, your email configuration is working correctly!</p>
            <p><strong>Server:</strong> Flask Backend</p>
            <p><strong>Time:</strong> {current_time}</p>
            """
        )

        mail.send(msg)
        print("✅ Test email sent successfully!")

        return jsonify({
            'success': True,
            'message': f'Test email sent successfully to {ADMIN_EMAIL}'
        }), 200

    except Exception as e:
        print(f"❌ Test email failed: {str(e)}")
        return jsonify({
            'error': f'Test email failed: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'mail_configured': bool(os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD')),
        'admin_email': ADMIN_EMAIL
    }), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Manejar rate limiting"""
    return jsonify({
        'error': 'Too many requests. Please try again later.'
    }), 429


if __name__ == '__main__':
    # Verificar variables de entorno requeridas
    required_env_vars = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'ADMIN_EMAIL']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"⚠️  WARNING: Missing environment variables: {missing_vars}")
        print("⚠️  Email functionality may not work properly")
    else:
        print("✅ All required environment variables are set")

    print("🚀 Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)