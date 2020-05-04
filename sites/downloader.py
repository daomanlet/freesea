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
        while True:
            future = self._rets.get()
            ret = future.result()
            print(ret)
            sendMail = EmailService()
            sendMail.sendMail(ret['email'], ret['rets'])
            time.sleep(1)
   

    def downloadThread(self, url, keyword, name):
        path = os.path.join(os.path.join(Config.VIDEO_WEBDAV, name), keyword)
        Path(path).mkdir(parents=True, exist_ok=True)
        ydl_opts = {
            'outtmpl': os.path.join(path, "%(title)s.%(ext)s"),
            'writesubtitles': True,
            'writethumbnail': True,
            "max_downloads": 1
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            res = { 'email':name,'rets':None}
            try:
                res['rets'] = ydl.extract_info(url, force_generic_extractor=ydl.params.get(
                    'force_generic_extractor', False))
                
            except MaxDownloadsReached:
                ydl.to_screen('[info] Maximum number of downloaded files reached.')
        return res

    def submitDownloadTask(self, site, url, keyword, useremail):
        executor = self._domainExecutor[site]
        try:
            args = [self, url, keyword, useremail]
            future = executor.submit(lambda p: DownloadService.downloadThread(*p),args)
            self._rets.put(future)
        except Exception as ex:
            print(ex)
        return
    
    def shutdown(self):
        self._thread._stop()
        
        return 
