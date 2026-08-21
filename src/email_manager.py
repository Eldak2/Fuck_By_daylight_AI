import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from src.settings_manager import SettingsManager

logger = logging.getLogger(__name__)
settings = SettingsManager()

class EmailManager:
    def __init__(self):
        self.smtp_server = settings.get("email_smtp_server")
        self.smtp_port = settings.get("email_smtp_port")
        self.imap_server = settings.get("email_imap_server")
        self.username = settings.get("email_username")
        self.password = settings.get("email_password")

    def is_configured(self):
        return bool(self.username and self.password)

    def send_email(self, to, subject, body, html=False):
        if not self.is_configured():
            return "Не настроен email (укажи логин и пароль в настройках)"
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return "Письмо отправлено"
        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            return f"Ошибка: {e}"

    def get_last_emails(self, limit=5):
        if not self.is_configured():
            return "Не настроен email"
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select('inbox')
            status, data = mail.search(None, 'UNSEEN')
            if status != 'OK':
                return "Нет новых писем"
            ids = data[0].split()
            if not ids:
                return "Нет новых писем"
            # берём последние `limit`
            ids = ids[-limit:]
            result = []
            for eid in ids:
                status, msg_data = mail.fetch(eid, '(RFC822)')
                if status != 'OK':
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg['Subject']
                from_ = msg['From']
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                result.append(f"От: {from_}\nТема: {subject}\n{body[:200]}...")
            mail.close()
            mail.logout()
            return "\n\n".join(result)
        except Exception as e:
            logger.error(f"Ошибка чтения почты: {e}")
            return f"Ошибка: {e}"