import smtplib
import ssl
from app.config import Config
from email.mime.text import MIMEText
from email.header import Header


class EmailService():
    _port = Config.SMTP_SERVER_PORT  # For SSL
    _smtp_server = Config.SMTP_SERVER
    _sender_email = Config.ADMIN_EMAIL  # Enter your address
    _password = Config.ADMIN_EMAIL_PASSCODE

    def __init__(self):
        pass

    def sendMail(self, receiver_email, content):
        if receiver_email is None:
            return
        template = '下载完成啦，请下载seafile app, 按照如下url连接您的网盘，用户名密码与您注册的一致\n'
        content = template + content 
        message = MIMEText(content, 'plain', 'utf-8')

        message['From'] = Header("自由海管理员", 'utf-8')
        message['To'] = Header(receiver_email, 'utf-8')

        subject = '下载完成通知'  # 发送的主题，可自由填写
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL(self._smtp_server, self._port)
            smtpObj.login(self._sender_email, self._password)
            smtpObj.sendmail(self._sender_email,
                             receiver_email, message.as_string())
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print('failed to send email')
