import os
import time
import threading, queue
import youtube_dl
import itertools
from sites import siteconfig
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from youtube_dl.utils import MaxDownloadsReached, ExtractorError, GeoRestrictedError, orderedSet
from app.config import Config
from app.email import EmailService


class DownloadService():

    _domainExecutor = {}
    _rets = queue.Queue()
    _thread = None
    
    def __init__(self):
        for site in siteconfig.SitesAvailable:
            executor = ThreadPoolExecutor(max_workers=site['thread_pool_size'])
            self._domainExecutor[site['name']]=executor
        _thread = threading.Thread(target=DownloadService.dealDownloadResults, args={self}, daemon=True)
        _thread.start()

    def dealDownloadResults(self):
        content = ''
        while True:
            future = self._rets.get()
            ret = future.result()
            print(ret)
            sendMail = EmailService()
            i = 1
            for entry in ret['rets']:
                content += str(i) + '. ' + entry['title'] + '\n'
                i += 1
            sendMail.sendMail(ret['email'], content)
            time.sleep(1)
   

    def downloadThread(self, site, url, keyword, name):
        siteConfig = siteconfig.findAvailableSiteConfigure(site)
        path = os.path.join(os.path.join(Config.VIDEO_WEBDAV, name), keyword)
        Path(path).mkdir(parents=True, exist_ok=True)
        ydl_opts = {
            'outtmpl': os.path.join(path, "%(title)s.%(ext)s"),
            'writesubtitles': True,
            'writethumbnail': True,
            "max_downloads": siteConfig['max_download']
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            res = {'email': name, 'rets': None}
            # res['rets'] = ydl.extract_info(url, force_generic_extractor=ydl.params.get(
            #     'force_generic_extractor', False))
            ies = ydl._ies
            for ie in ies:
                if not ie.suitable(url) or ie.IE_NAME == 'generic':
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
                    break
                except GeoRestrictedError as e:
                    break
                except ExtractorError as e:  # An error we somewhat expected
                    break
                except MaxDownloadsReached:
                    ydl.to_screen(
                        '[info] Maximum number of downloaded files reached.')
                    break
                except Exception as e:
                    continue
        return res

    def submitDownloadTask(self, site, url, keyword, useremail):
        executor = self._domainExecutor[site]
        try:
            args = [self, site, url, keyword, useremail]
            future = executor.submit(lambda p: DownloadService.downloadThread(*p),args)
            self._rets.put(future)
        except Exception as ex:
            print(ex)
        return
    
    def shutdown(self):
        self._thread._stop()
        
        return 
