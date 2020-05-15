import os
import uuid
import threading
import traceback
import imgkit
from pathlib import Path
from flask import render_template, json, request, send_file, url_for, redirect, flash
from flask_login import current_user, login_user, logout_user
import youtube_dl
from youtube_dl.utils import MaxDownloadsReached
from app.config import Config
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.webdav import WebDAV
from app.email import EmailService
from app import app, db
from sites import siteconfig
from sites.downloader import DownloadService
from concurrent.futures import ThreadPoolExecutor
import threading, queue
import time

_downloadSrv = None 
_webDav = None

@app.route('/search', methods=['GET'])
def dark_search():
    site = 'youtube'
    keyword = request.args.get('keywords')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['search_url'] + keyword
    else :
        url = "https://www.youtube.com/results?search_query="+keyword
        site= 'youtube'        
        ##url = "https://cn.pornhub.com/video/search?search="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    userfolder = os.path.join(Config.IMG_CACHE, name)
    Path(userfolder).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(userfolder, str(uuid.uuid4())+site+'.jpg')
    if not os.path.exists(filename):
        options = {}
        if os.name != 'nt':
            options = {
                'quiet': '',
                "xvfb": ''
            }
        imgkit.from_url(url, filename, options=options)
        _downloadSrv.submitDownloadTask(site, url, keyword, name)
    return send_file(filename, mimetype='image/jpg')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        _webDav = WebDAV()
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


@app.route("/register", methods=["GET", "POST"])
def user_register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        webdav = WebDAV()
        webdav.addUser(form.email.data, form.password.data)
        webdav.shareFolder(Config.COMMUNITY_VERSION_SHARE_LIBRARY, form.email.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/about", methods=["GET", "POST"])
def getAbout():
    if current_user.is_authenticated:
        name = current_user.email
    else:
        name = 'xxx@qq.com'    
    config = {}
    config['webdavurl'] = Config.REMOTE_STORAGE_URL
    config['name'] = name
    return render_template('about.html', title='Register', conf=config)

@app.route("/filelist", methods=["GET", "POST"])
def list_file():
    if current_user.is_authenticated:
        name = current_user.email
    else:
        return redirect(url_for('login'))    
    userfolder = os.path.join(Config.VIDEO_WEBDAV, name)
    files = []
    for root, dirs, fps in os.walk(userfolder):    
        for path in dirs:
            tag = path
            fullpath = os.path.join(userfolder,path)
            for file in os.listdir(os.path.join(userfolder,path)):
                if file.endswith(".jpg"):
                    temp = {}
                    temp['tag'] = tag
                    temp['img'] = "/"+os.path.basename(Config.VIDEO_WEBDAV)+"/"+name+"/"+file
                    temp['title'] = os.path.splitext(file)[0]
                    mediafile = os.path.join(fullpath, temp['title']+'.mp4')
                    if os.path.exists(mediafile):
                        temp['link'] = "/"+os.path.basename(Config.VIDEO_WEBDAV)+"/"+name+"/"+temp['title']+'.mp4'
                        files.append(temp)
                    else:
                        mediafile = os.path.join(fullpath, temp['title']+'.mkv')
                        if os.path.exists(mediafile):
                            temp['link'] = "/"+os.path.basename(Config.VIDEO_WEBDAV)+"/"+name+"/"+temp['title']+'.mkv'
                        files.append(temp)
    return render_template('filelist.html', title='Files', files=files)

@app.route('/')
@app.route('/index')
def root():
    return render_template('index.html', title='Home')

if __name__ == '__main__':
    db.create_all()
    _downloadSrv = DownloadService()
    app.run(host='0.0.0.0',
            port=7777, debug=True)
    _downloadSrv.shutdown()