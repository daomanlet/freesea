import smtplib
import ssl
from app.config import Config

class EmailService():
    _port = Config.SMTP_SERVER_PORT  # For SSL
    _smtp_server = Config.SMTP_SERVER
    _sender_email = Config.ADMIN_EMAIL  # Enter your address
    _password = Config.ADMIN_EMAIL_PASSCODE

    def __init__(self):
        pass

    def sendMail(self, receiver_email, message):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self._smtp_server, self._port, context=context) as server:
            server.login(self._sender_email, self._password)
            server.sendmail(self._sender_email, receiver_email, message)
