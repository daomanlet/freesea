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
    