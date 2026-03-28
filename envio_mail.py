import csv
import os
import base64
import smtplib
import ssl
import time
from email.message import EmailMessage

# CONFIGURACIÓN SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "authsmtp.securemail.pro")
# Por defecto, STARTTLS en 587. Si tu proveedor requiere SSL implícito en 465,
# exporta SMTP_USE_SSL=1 y opcionalmente SMTP_PORT=465.
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "0") == "1"
# Toma credenciales de variables de entorno si existen; de lo contrario usa los valores actuales.
EMAIL_USER = os.getenv("EMAIL_USER", "info@theperfectplacegolf.es")
EMAIL_PASS = os.getenv("EMAIL_PASS", "Tppg2026.")
SMTP_DEBUG = os.getenv("SMTP_DEBUG", "0") == "1"

# CONFIGURACIÓN ENVÍO
CSV_FILE = "contactos.csv"
MAX_EMAILS = 2  # 1 hora = 60 emails
DELAY = 30  # segundos

# PLANTILLAS
SUBJECT_TEMPLATE = "A la atención de: {at}"
BODY_TEMPLATE = """Hola {nombre},

Este es un mensaje automático.

Saludos,
Tu empresa
"""

def _auth_login_login_mechanism(server: smtplib.SMTP, user: str, password: str) -> bool:
    """Intenta AUTH LOGIN manual para sortear desconexiones durante login()."""
    try:
        code, _ = server.docmd("AUTH", "LOGIN")
        if code != 334:
            return False
        code, _ = server.docmd(base64.b64encode(user.encode()).decode())
        if code != 334:
            return False
        code, _ = server.docmd(base64.b64encode(password.encode()).decode())
        return code == 235
    except Exception:
        return False


def _login_with_fallback(server: smtplib.SMTP) -> None:
    """Primero intenta server.login; si el servidor cierra, intenta AUTH LOGIN manual."""
    try:
        server.login(EMAIL_USER, EMAIL_PASS)
        return
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPAuthenticationError):
        # Intento manual AUTH LOGIN
        if _auth_login_login_mechanism(server, EMAIL_USER, EMAIL_PASS):
            return
        raise


def enviar_emails():
    context = ssl.create_default_context()

    # Conexión según configuración
    if SMTP_USE_SSL:
        server: smtplib.SMTP
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
            if SMTP_DEBUG:
                server.set_debuglevel(1)
            server.ehlo()
            _login_with_fallback(server)
            
            with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for i, row in enumerate(reader):
                    if i >= MAX_EMAILS:
                        print("⏹ Límite alcanzado (1 hora)")
                        break

                    email_destino = row["email"]
                    nombre = row["nombre"]
                    at = row["at"]

                    subject = SUBJECT_TEMPLATE.format(at=at)
                    body = BODY_TEMPLATE.format(nombre=nombre)

                    msg = EmailMessage()
                    msg["From"] = EMAIL_USER
                    msg["To"] = email_destino
                    msg["Subject"] = subject
                    msg.set_content(body)

                    try:
                        server.send_message(msg)
                        print(f"✅ Enviado a {email_destino}")
                    except Exception as e:
                        print(f"❌ Error con {email_destino}: {e}")

                    time.sleep(DELAY)
    else:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            if SMTP_DEBUG:
                server.set_debuglevel(1)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            _login_with_fallback(server)

            with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for i, row in enumerate(reader):
                    if i >= MAX_EMAILS:
                        print("⏹ Límite alcanzado (1 hora)")
                        break

                    email_destino = row["email"]
                    nombre = row["nombre"]
                    at = row["at"]

                    subject = SUBJECT_TEMPLATE.format(at=at)
                    body = BODY_TEMPLATE.format(nombre=nombre)

                    msg = EmailMessage()
                    msg["From"] = EMAIL_USER
                    msg["To"] = email_destino
                    msg["Subject"] = subject
                    msg.set_content(body)

                    try:
                        server.send_message(msg)
                        print(f"✅ Enviado a {email_destino}")
                    except Exception as e:
                        print(f"❌ Error con {email_destino}: {e}")

                    time.sleep(DELAY)

if __name__ == "__main__":
    enviar_emails()