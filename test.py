from app.remote_storage import RemoteStorage
from app.webdav import WebDAV
from app.email import EmailService
import sys
import youtube_dl
from youtube_dl.utils import MaxDownloadsReached, ExtractorError, GeoRestrictedError, orderedSet
import os
import itertools


def testWebdavStorage():
    webdav = WebDAV()
    ret = webdav.addUser('xia_zheny@hotmail.com', 'Welcome1')
    print(ret)


def testEmail():
    email = EmailService()
    email.sendMail('xia_zhenyu@hotmail.com', '中文内容')


def testDownload():
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
    testDownload()
