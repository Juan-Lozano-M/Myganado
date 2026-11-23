"""Persisted SMTP delivery; missing configuration remains visible in the audit trail."""
import os
import smtplib
from email.message import EmailMessage

from app.services.repository import Repository


class NotificationService:
    def __init__(self, repository: Repository | None = None) -> None:
        self.repository = repository or Repository()

    def dispatch_for_prediction(self, prediction_id: int) -> None:
        for notification in self.repository.pending_notifications(prediction_id):
            host = os.environ.get("MYGANADO_SMTP_HOST")
            sender = os.environ.get("MYGANADO_SMTP_FROM")
            if not host or not sender:
                self.repository.update_notification(notification["id"], "sin_configurar", "Configura MYGANADO_SMTP_HOST y MYGANADO_SMTP_FROM")
                continue
            message = EmailMessage()
            message["From"] = sender
            message["To"] = notification["recipient_email"]
            message["Subject"] = f"My Ganado: seguimiento de {notification['animal_id']}"
            message.set_content(
                f"Hay una alerta de seguimiento para {notification['animal_id']}. "
                "Ingresa a My Ganado para revisar el historial. "
                "Este aviso no es un diagnóstico veterinario."
            )
            try:
                port = int(os.environ.get("MYGANADO_SMTP_PORT", "587"))
                with smtplib.SMTP(host, port, timeout=8) as client:
                    client.starttls()
                    username = os.environ.get("MYGANADO_SMTP_USER")
                    password = os.environ.get("MYGANADO_SMTP_PASSWORD")
                    if username and password:
                        client.login(username, password)
                    client.send_message(message)
                self.repository.update_notification(notification["id"], "enviada")
            except (OSError, smtplib.SMTPException, ValueError) as exc:
                self.repository.update_notification(notification["id"], "fallida", str(exc)[:500])
