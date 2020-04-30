import os
import pathlib 


basedir = pathlib.Path().absolute()

class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    IMG_CACHE = os.path.join(basedir, 'img')

    VIDEO_WEBDAV = os.path.join(basedir, 'video')

    REMOTE_STORAGE_URL = 'http://192.168.2.22'
    REMOTE_STORAGE_USER = 'xiazheny@gmail.com'
    REMOTE_STORAGE_PWD = 'Welcome1'
    
    # community edition using default share library to make other users check download files
    COMMUNITY_VERSION_SHARE_LIBRARY = 'video'  

    #SMTP Server
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_SERVER_PORT = 465
    ADMIN_EMAIL = 'xiazheny@gmail.com'
    ADMIN_EMAIL_PASSCODE = '9post96423'