import csv
import smtplib
import ssl
import time
from email.message import EmailMessage

# CONFIGURACIÓN SMTP
SMTP_SERVER = "authsmtp.securemail.pro"
SMTP_PORT = 465
EMAIL_USER = "info@theperfectplacegolf.es"
EMAIL_PASS = "Tppg2026."

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

def enviar_emails():
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(EMAIL_USER, EMAIL_PASS)

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