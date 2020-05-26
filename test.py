from app.remote_storage import RemoteStorage
from app.webdav import WebDAV
from app.email import EmailService
from app.config import Config
from sites import siteconfig
from sites.downloader import DownloadService
import sys
import youtube_dl
from youtube_dl.utils import (
    MaxDownloadsReached,
    ExtractorError,
    GeoRestrictedError,
    orderedSet,
    sanitize_url,
    url_basename,
    ISO3166Utils,
    error_to_compat_str,
    encode_compat_str,
    compat_str,
    PagedList)
import os
import random
import itertools
import time
import traceback
from flask import jsonify
from pathlib import Path


def testWebdavStorage():
    webdav = WebDAV()
    ret = webdav.addUser('xia_zheny@hotmail.com', 'Welcome1')
    print(ret)


def testDownloadRedirect():
    path = os.path.join(os.path.join(Config.VIDEO_WEBDAV,
                                     "xia_zhenyu@hotmail.com"), "徐克")
    Path(path).mkdir(parents=True, exist_ok=True)
    srv = DownloadService()
    srv.downloadVideo(
        'https://cn.pornhub.com/view_video.php?viewkey=ph5e6ef9a6c3d18', path, True)


def testEmail():
    email = EmailService()
    email.sendMail('xia_zhenyu@hotmail.com', '中文内容')


def selectExtractor(ies, url):
    for ie in ies:
        if ie.suitable(url):
            return ie
    return None


def testYoutubeDL_youtube_channel():
    srv = DownloadService()
    entries = srv.extractChannelSubscription('https://www.youtube.com/channel/UCoC47do520os_4DBMEFGg4A')
    assert(entries)
    return 


def testDownloadPornHub():
    path = os.path.join(os.path.join(Config.VIDEO_WEBDAV,
                                     "xia_zhenyu@hotmail.com"), "徐克")
    Path(path).mkdir(parents=True, exist_ok=True)
    srv = DownloadService()
    res = srv.extractSearchSubscription(
        'https://cn.pornhub.com/video/search?search=%E9%9F%A9%E5%9B%BD', 'xia_zhenyu@hotmail.com')
    ret = srv.extractPlayListDetail(res['rets'], 10, './', False)
    ret = srv.extractPlayListDetail(res['rets'], 1, './', True)
    print(ret)


def testDownloadYoutube():
    path = os.path.join(os.path.join(Config.VIDEO_WEBDAV,
                                     "xia_zhenyu@hotmail.com"), "徐克")
    Path(path).mkdir(parents=True, exist_ok=True)

    srv = DownloadService()
    # res = srv.extractSearchSubscription('https://www.youtube.com/results?search_query=%E5%BE%90%E5%85%8B','xia_zhenyu@hotmail.com')
    res = srv.extractSearchSubscription(
        'https://www.youtube.com/channel/UCoC47do520os_4DBMEFGg4A', 'xia_zhenyu@hotmail.com')
    ret = srv.extractPlayListDetail(res['rets'], 10, './', False)
    ret = srv.extractPlayListDetail(res['rets'], 1, './', True)

    print(ret)
    return

def testDownloadMP3():
    url = 'https://www.youtube.com/watch?v=UekXkqU_yIA'
    srv = DownloadService()
    srv.downloadVideo(url, Path().absolute(), download=True, format='mp3')

def testDownloadDetail():
    name = 'xia_zhenyu@hotmail.com'
    url = 'https://www.youtube.com/results?search_query=%E5%BE%90%E5%85%8B'
    ydl_opts = {
        'outtmpl': os.path.join('./', "%(title)s.%(ext)s"),
        'writesubtitles': True,
        'writethumbnail': True,
        "max_downloads": 1
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = {'email': name, 'rets': None}
        # res['rets'] = ydl.extract_info(url, force_generic_extractor=ydl.params.get(
        #     'force_generic_extractor', False))
        ies = ydl._ies
        for ie in ies:
            if not ie.suitable(url):
                continue
            ie = ydl.get_info_extractor(ie.ie_key())
            if not ie.working():
                ydl.report_warning('The program functionality for this site has been marked as broken, '
                                   'and will probably not work.')
            try:
                ie_result = ie.extract(url)
                if ie_result is None:
                    break
                if isinstance(ie_result, list):
                    ie_result = {
                        '_type': 'compat_list',
                        'entries': ie_result,
                    }
                ydl.add_default_extra_info(ie_result, ie, url)
                ie_entries = ie_result['entries']
                res['rets'] = list(itertools.islice(
                    ie_entries, 0, None))
                ydl.process_ie_result(ie_result, True, {})
            except GeoRestrictedError as e:
                break
            except ExtractorError as e:  # An error we somewhat expected
                break
            except MaxDownloadsReached:
                ydl.to_screen(
                    '[info] Maximum number of downloaded files reached.')
            except Exception as e:
                if ydl.params.get('ignoreerrors', False):
                    break
                else:
                    raise
    return res


if __name__ == '__main__':
    # testDownloadPornHub()
    # testDownloadRedirect()
    # testDownloadYoutube()
    # testYoutubeDL_youtube_channel()
    testDownloadMP3()
