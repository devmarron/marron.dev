# marron.dev Backend - Contact Form API

Backend en Python Flask para manejar el formulario de contacto de marron.dev con funcionalidades avanzadas de email y validación.

## 🚀 Características

- ✅ **Formulario de contacto funcional** con validación completa
- 📧 **Sistema de emails** con templates HTML profesionales
- 🛡️ **Rate limiting** para prevenir spam
- 🎨 **Emails con diseño** que mantienen la identidad visual
- ⚡ **Confirmación automática** al cliente
- 🔍 **Validación robusta** de datos
- 📱 **CORS configurado** para frontend

## 🛠️ Instalación

### 1. Clonar y preparar entorno

```bash
# Crear directorio para el backend
mkdir marron-dev-backend
cd marron-dev-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

### 4. Configurar Gmail (recomendado)

Para usar Gmail como servidor SMTP:

1. **Habilita 2FA** en tu cuenta de Gmail
2. **Genera App Password**:
   - Ve a Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Genera password para "Mail"
3. **Configura en .env**:
   ```bash
   MAIL_USERNAME=tu-email@gmail.com
   MAIL_PASSWORD=tu-app-password-generado
   ```

## 🔧 Configuración

### Variables de entorno principales:

```bash
# Email configuration
MAIL_USERNAME=hello@marron.dev
MAIL_PASSWORD=tu-app-password

# Admin email (donde llegan los mensajes)
ADMIN_EMAIL=admin@marron.dev

# CORS (dominios permitidos)
ALLOWED_ORIGINS=https://marron.dev,https://www.marron.dev
```

## ▶️ Ejecutar en desarrollo

```bash
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

## 🚀 Ejecutar en producción

### Con Gunicorn:

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Con Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📡 API Endpoints

### POST /api/contact

Envía un mensaje de contacto.

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "company": "Acme Corp",
  "projectType": "web-development",
  "budget": "15k-30k",
  "message": "Necesitamos una nueva web..."
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Thank you! We'll get back to you within 24 hours."
}
```

**Response Error (400):**
```json
{
  "errors": {
    "email": "Invalid email format",
    "message": "Message is required"
  }
}
```

### GET /api/health

Health check del servidor.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00"
}
```

## 🔒 Seguridad

- **Rate limiting**: 5 submissions por minuto por IP
- **Input sanitization**: Limpieza automática de datos
- **Email validation**: Validación robusta de formato
- **CORS configurado**: Solo dominios permitidos

## 📧 Templates de Email

### Email al Admin:
- Diseño profesional con colores de marron.dev
- Información completa del cliente
- Detalles del proyecto
- Timestamp de envío

### Email de Confirmación:
- Mensaje personalizado al cliente
- Call-to-action al portfolio
- Información de contacto
- Branding consistente

## 🐛 Troubleshooting

### Error: "Failed to send email"
- Verifica credenciales de Gmail
- Confirma que 2FA está habilitado
- Revisa que App Password sea correcto

### Error: "CORS origin not allowed"
- Añade tu dominio en `ALLOWED_ORIGINS`
- En desarrollo usa `http://localhost:3000`

### Error: "Rate limit exceeded"
- Espera 1 minuto entre submissions
- En desarrollo puedes desactivar rate limiting

## 📝 Personalización

### Cambiar templates de email:
Modifica las funciones `create_email_template()` y `create_client_confirmation_email()` en `app.py`

### Añadir campos al formulario:
1. Actualiza el HTML del formulario
2. Añade validación en `validate_contact_data()`
3. Incluye en los templates de email

### Configurar otros proveedores de email:
```python
# Para SendGrid
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587

# Para Mailgun
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
```

## 📈 Monitoreo

El backend incluye logging automático:
- Submissions exitosos
- Errores de email
- Rate limiting
- Validación fallida

## 🤝 Soporte

Para soporte técnico:
- Email: hello@marron.dev
- Issues: GitHub repository

---

**marron.dev** - Digital Innovation Studio