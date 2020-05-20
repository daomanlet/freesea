import os
import uuid
import threading
import traceback
import imgkit
import requests
from pathlib import Path
from flask import (
    render_template,
    json,
    request,
    Response,
    send_file,
    url_for,
    redirect,
    flash,
    jsonify,
    session,
    abort, g,
    send_from_directory)
from flask_login import current_user, login_user, logout_user
import youtube_dl
from youtube_dl.utils import MaxDownloadsReached
from app.config import Config
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.webdav import WebDAV
from app.email import EmailService
from app import app, db, create_app, downloader
from sites import siteconfig
from sites.downloader import DownloadService
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time
import itertools
import re


@app.route('/search', methods=['GET'])
def dark_search():
    site = 'youtube'
    keyword = request.args.get('keywords')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['search_url'] + keyword
    else:
        url = "https://www.youtube.com/results?search_query="+keyword
        site = 'youtube'
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
#        app.get_download_service.submitDownloadTask(site, url, keyword, name)
    return send_file(filename, mimetype='image/jpg')


@app.route('/download', methods=["GET"])
def download():
    site = 'youtube'
    keyword = request.args.get('id')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['video_url'] + keyword
    else:
        url = "https://www.youtube.com/watch?v="+keyword
        site = 'youtube'
        ##url = "https://cn.pornhub.com/video/search?search="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    userfolder = os.path.join(Config.VIDEO_WEBDAV, name)
    Path(userfolder).mkdir(parents=True, exist_ok=True)
    ie_result = downloader.downloadVideo(url, userfolder, True)
    fileName = ie_result['title']+'.mp4'
    try:
        return send_from_directory(userfolder, filename=fileName, as_attachment=True)
    except FileNotFoundError:
        abort(404)

def get_chunk(byte1, byte2, fileName):
    full_path = fileName
    file_size = os.stat(full_path).st_size
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


@app.route('/stream', methods=["GET"])
def stream():
    site = 'youtube'
    keyword = request.args.get('id')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['video_url'] + keyword
    else:
        url = "https://www.youtube.com/watch?v="+keyword
        site = 'youtube'
        ##url = "https://cn.pornhub.com/video/search?search="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    userfolder = os.path.join(Config.VIDEO_WEBDAV, name)
    Path(userfolder).mkdir(parents=True, exist_ok=True)
    ie_result = downloader.downloadVideo(url, userfolder, True)
    fileName = os.path.join(userfolder, ie_result['title']+'.mp4')
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()
        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(byte1, byte2, fileName)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


@app.route('/detail', methods=["GET", "POST"])
def getDetail():
    site = 'youtube'
    keyword = request.args.get('id')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['video_url'] + keyword
    else:
        url = "https://www.youtube.com/watch?v="+keyword
        site = 'youtube'
        ##url = "https://cn.pornhub.com/video/search?search="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    userfolder = os.path.join(Config.VIDEO_WEBDAV, name)
    Path(userfolder).mkdir(parents=True, exist_ok=True)
    ret = downloader.downloadVideo(url, userfolder)
    return jsonify(ret), 200


@app.route('/subscribe', methods=['GET'])
def getSubscribeList():
    site = 'youtube'
    keyword = request.args.get('keywords')
    site = request.args.get('domain')
    siteConfig = siteconfig.findAvailableSiteConfigure(site)
    if siteConfig is not None:
        url = siteConfig['search_url'] + keyword
    else:
        url = "https://www.youtube.com/results?search_query="+keyword
        site = 'youtube'
        ##url = "https://cn.pornhub.com/video/search?search="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    future = downloader.submitSubscribeTask(url, 'youtube', name)
    ret = future.result()
    session['ie_result'] = ret
    return jsonify(list(itertools.islice(ret['rets']['entries'], 0, None))), 200


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
        try:
            if session['webdav'] is not None:
                session.pop('webdav')
            session['webdav'] = webDav 
        except:
            pass
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
        try:
            webdav = WebDAV()
            webdav.addUser(form.email.data, form.password.data)
            webdav.shareFolder(
                Config.COMMUNITY_VERSION_SHARE_LIBRARY, form.email.data)
        except:
            pass
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
            fullpath = os.path.join(userfolder, path)
            for file in os.listdir(os.path.join(userfolder, path)):
                if file.endswith(".jpg"):
                    temp = {}
                    temp['tag'] = tag
                    temp['img'] = "/" + \
                        os.path.basename(Config.VIDEO_WEBDAV)+"/"+name+"/"+file
                    temp['title'] = os.path.splitext(file)[0]
                    mediafile = os.path.join(fullpath, temp['title']+'.mp4')
                    if os.path.exists(mediafile):
                        temp['link'] = "/"+os.path.basename(
                            Config.VIDEO_WEBDAV)+"/"+name+"/"+temp['title']+'.mp4'
                        files.append(temp)
                    else:
                        mediafile = os.path.join(
                            fullpath, temp['title']+'.mkv')
                        if os.path.exists(mediafile):
                            temp['link'] = "/"+os.path.basename(
                                Config.VIDEO_WEBDAV)+"/"+name+"/"+temp['title']+'.mkv'
                        files.append(temp)
    return render_template('filelist.html', title='Files', files=files)


@app.route('/')
@app.route('/index')
def root():
    return render_template('index.html', title='Home')


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', threaded=True,
            port=7777, debug=True)
