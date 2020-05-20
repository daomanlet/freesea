#!/usr/bin/env python
# coding: utf-8
from flask import (Flask,g)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
from sites.downloader import DownloadService

app = Flask(__name__)
db = SQLAlchemy(app)
downloader = DownloadService()
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
app.config.from_object(Config)

# def get_downloader():
#     if 'downloader' not in g:
#         g.downloader = 
#     return g.downloader

def create_app():
    db.create_all()
    return app    
