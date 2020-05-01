from app.remote_storage import RemoteStorage
from app.webdav import WebDAV
from app.email import EmailService
import sys

def testWebdavStorage():
    webdav = WebDAV()
    ret = webdav.addUser('xia_zheny@hotmail.com','Welcome1')
    print(ret)

def testEmail():
    email = EmailService()
    email.sendMail('xia_zhenyu@hotmail.com','中文内容')

if __name__ == '__main__':
    testEmail()
    
    
