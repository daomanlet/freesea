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
from app import app, db


@app.route('/downloads', methods=['GET'])
def get_downloads():
    url = request.args.get('url')
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(url, force_generic_extractor=ydl.params.get(
            'force_generic_extractor', False))
    return json.dumps(res)


def downloadThread(url, keyword, name):
    path = os.path.join(os.path.join(Config.VIDEO_WEBDAV, name), keyword)
    Path(path).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(path, "%(title)s.%(ext)s"),
        'writesubtitles': True,
        'writethumbnail': True,
        "max_downloads": 1
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = None
        try:
            res = ydl.extract_info(url, force_generic_extractor=ydl.params.get(
                'force_generic_extractor', False))
        except MaxDownloadsReached:
            ydl.to_screen('[info] Maximum number of downloaded files reached.')
    return res


@app.route('/search', methods=['GET'])
def dark_search():
    keyword = request.args.get('keywords')
    ##url = "https://cn.pornhub.com/video/search?search="+keyword
    url = "https://www.youtube.com/results?search_query="+keyword
    name = ""
    if current_user.is_authenticated:
        name = current_user.email
    userfolder = os.path.join(Config.IMG_CACHE, name)
    Path(userfolder).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(userfolder, str(uuid.uuid4())+'.jpg')
    ##filename = str(uuid.uuid4())+'.jpg'
    if not os.path.exists(filename):
        options = {}
        if os.name != 'nt':
            options = {
                'quiet': '',
                "xvfb": ''
            }
        imgkit.from_url(url, filename, options=options)
        try:
            t_temp = threading.Thread(
                target=downloadThread, args=(url, keyword, name))
            t_temp.start()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
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


@app.route('/')
@app.route('/index')
def root():
    return render_template('index.html', title='Home')


if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1',
            port=7777, debug=True)
