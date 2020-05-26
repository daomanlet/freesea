import os
import sys
import traceback
import time
import threading
import queue
import youtube_dl
import random
import itertools
from sites import siteconfig
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from youtube_dl.utils import (
    PagedList,
    MaxDownloadsReached,
    ExtractorError,
    GeoRestrictedError,
    orderedSet,
    url_basename,
    sanitize_url,
    ISO3166Utils,
    error_to_compat_str,
    encode_compat_str,
    compat_str,
    PagedList)
from app.config import Config
from app.email import EmailService


class DownloadService():

    _domainExecutor = {}
    _rets = queue.Queue()
    _thread = None

    def __init__(self):
        for site in siteconfig.SitesAvailable:
            executor = ThreadPoolExecutor(max_workers=site['thread_pool_size'])
            self._domainExecutor[site['name']] = executor
        _thread = threading.Thread(
            target=DownloadService.dealDownloadResults, args={self}, daemon=True)
        _thread.start()

    def dealDownloadResults(self):
        content = ''
        # TODO: send email after download completed
        while True:
            # future = self._rets.get()
            # ret = future.result()
            # print(ret)
            # sendMail = EmailService()
            # i = 1
            # for entry in ret['rets']:
            #     try:
            #         content += str(i) + '. ' + entry['title'] + '\n'
            #     except:
            #         traceback.print_exc(file=sys.stdout)
            #     i += 1
            # sendMail.sendMail(ret['email'], content)
            time.sleep(1)

    def downloadVideo(self, url, path, download=False, format='mp4'):
        Path(path).mkdir(parents=True, exist_ok=True)
        fileName = os.path.join(path, "%(title)s.%(ext)s")
        if 'mp3' in format:
            ydl_opts = {
                'sleep-interval': 10,
                'outtmpl': fileName,
                'writesubtitles': True,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'writethumbnail': True
            }
        else:
            ydl_opts = {
                'sleep-interval': 10,
                'outtmpl': fileName,
                'writesubtitles': True,
                'format': 'mp4',
                'writethumbnail': True
            }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ie_result = ydl.extract_info(url, download)
        return ie_result

    def extractPlayListDetail(self,
                              ie_result, max_downloads, path='', download=False):
        ydl_opts = {
            'outtmpl': os.path.join(path, "%(title)s.%(ext)s"),
            'writesubtitles': True,
            'writethumbnail': True,
            # 'playlist_items': '2,3,7,10',
            "max_downloads": max_downloads
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result_type = ie_result.get('_type', 'video')
            if result_type in ('playlist', 'multi_video'):
                # We process each entry in the playlist
                playlist = ie_result.get('title') or ie_result.get('id')
                ydl.to_screen(
                    '[Extract Information] Extracting playlist: %s' % playlist)

                playlist_results = []

                playliststart = ydl.params.get('playliststart', 1) - 1
                playlistend = ydl.params.get('playlistend')
                # For backwards compatibility, interpret -1 as whole list
                if playlistend == -1:
                    playlistend = None

                playlistitems_str = ydl.params.get('playlist_items')
                playlistitems = None
                if playlistitems_str is not None:
                    def iter_playlistitems(format):
                        for string_segment in format.split(','):
                            if '-' in string_segment:
                                start, end = string_segment.split('-')
                                for item in range(int(start), int(end) + 1):
                                    yield int(item)
                            else:
                                yield int(string_segment)
                    playlistitems = orderedSet(
                        iter_playlistitems(playlistitems_str))

                ie_entries = ie_result['entries']

                def make_playlistitems_entries(list_ie_entries):
                    num_entries = len(list_ie_entries)
                    return [
                        list_ie_entries[i - 1] for i in playlistitems
                        if -num_entries <= i - 1 < num_entries]

                def report_download(num_entries):
                    ydl.to_screen(
                        '[%s] playlist %s: Extracting %d videos' %
                        (ie_result['extractor'], playlist, num_entries))

                if isinstance(ie_entries, list):
                    n_all_entries = len(ie_entries)
                    if playlistitems:
                        entries = make_playlistitems_entries(ie_entries)
                    else:
                        entries = ie_entries[playliststart:playlistend]
                    n_entries = len(entries)
                    ydl.to_screen(
                        '[%s] playlist %s: Collected %d video ids (extractng %d of them)' %
                        (ie_result['extractor'], playlist, n_all_entries, n_entries))
                elif isinstance(ie_entries, PagedList):
                    if playlistitems:
                        entries = []
                        for item in playlistitems:
                            entries.extend(ie_entries.getslice(
                                item - 1, item
                            ))
                    else:
                        entries = ie_entries.getslice(
                            playliststart, playlistend)
                    n_entries = len(entries)
                    report_download(n_entries)
                else:  # iterable
                    if playlistitems:
                        entries = make_playlistitems_entries(list(itertools.islice(
                            ie_entries, 0, max(playlistitems))))
                    else:
                        entries = list(itertools.islice(
                            ie_entries, playliststart, playlistend))
                    n_entries = len(entries)
                    report_download(n_entries)

                if ydl.params.get('playlistreverse', False):
                    entries = entries[::-1]

                if ydl.params.get('playlistrandom', False):
                    random.shuffle(entries)

                x_forwarded_for = ie_result.get('__x_forwarded_for_ip')
                for i, entry in enumerate(entries, 1):
                    ydl.to_screen(
                        '[extract information] Extracting video %s of %s' % (i, n_entries))
                    # This __x_forwarded_for_ip thing is a bit ugly but requires
                    # minimal changes
                    if x_forwarded_for:
                        entry['__x_forwarded_for_ip'] = x_forwarded_for
                    extra = {
                        'n_entries': n_entries,
                        'playlist': playlist,
                        'playlist_id': ie_result.get('id'),
                        'playlist_title': ie_result.get('title'),
                        'playlist_uploader': ie_result.get('uploader'),
                        'playlist_uploader_id': ie_result.get('uploader_id'),
                        'playlist_index': playlistitems[i - 1] if playlistitems else i + playliststart,
                        'extractor': ie_result['extractor'],
                        'webpage_url': ie_result['webpage_url'],
                        'webpage_url_basename': url_basename(ie_result['webpage_url']),
                        'extractor_key': ie_result['extractor_key'],
                    }

                    reason = ydl._match_entry(entry, incomplete=True)
                    if reason is not None:
                        ydl.to_screen('[Extract] ' + reason)
                        continue
                    try:
                        time.sleep(2000)
                        entry_result = ydl.process_ie_result(entry,
                                                             download=download,
                                                             extra_info=extra)
                    except MaxDownloadsReached:
                        ydl.to_screen(
                            '[info] Maximum number of downloaded files reached.')
                        break
                    playlist_results.append(entry_result)
                ie_result['entries'] = playlist_results
                ydl.to_screen(
                    '[Extract] Finished extracting playlist: %s' % playlist)
        return ie_result

    def _selectExtractor(self, ies, url):
        for ie in ies:
            if ie.suitable(url):
                return ie
        return None

    def extractChannelSubscription(self, url, user_name=None):
        entries = None
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            youtube_dl.utils.std_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            ie = self._selectExtractor(ydl._ies, url)
            if ie is None:
                return None
            ie = ydl.get_info_extractor(ie.ie_key())
            if not ie.working():
                ydl.report_warning('The program functionality for this site has been marked as broken, '
                                   'and will probably not work.')
            try:
                ie_result = ie.extract(url)
                if ie_result is None:
                    return None
                ydl.add_default_extra_info(ie_result, ie, url)
                # ydl.process_ie_result(ie_result)
                # here the url type changed, so we hava to select extractor again
                url = sanitize_url(ie_result['url'])
                ie = self._selectExtractor(ydl._ies, ie_result['url'])
                ie = ydl.get_info_extractor(ie.ie_key())
                ie_result = ie.extract(url)
                ie_entries = ie_result['entries']
                entries = list(itertools.islice(ie_entries, 0, None))
            except GeoRestrictedError as e:
                msg = e.msg
                if e.countries:
                    msg += '\nThis video is available in %s.' % ', '.join(
                        map(ISO3166Utils.short2full, e.countries))
                msg += '\nYou might want to use a VPN or a proxy server (with --proxy) to workaround.'
                ydl.report_error(msg)
            except ExtractorError as e:  # An error we somewhat expected
                ydl.report_error(compat_str(e), e.format_traceback())
            except MaxDownloadsReached:
                raise
            except Exception as e:
                if ydl.params.get('ignoreerrors', False):
                    ydl.report_error(error_to_compat_str(
                        e), tb=encode_compat_str(traceback.format_exc()))
                    return None
                else:
                    raise
        return entries

    def extractSearchSubscription(self, url, user_name):
        ydl_opts = {
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            res = {'email': user_name, 'rets': None}
            youtube_dl.utils.std_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            if 'youtube' in url:
                res['rets'] = ydl.extract_info(
                    url, download=False, process=True)
            else:
                res['rets'] = ydl.extract_info(
                    url, download=False, process=False)
        return res

    def submitSubscribeTask(self, url, site, user_name):
        executor = self._domainExecutor[site]
        try:
            args = [self, url, user_name]
            future = executor.submit(
                lambda p: DownloadService.extractSearchSubscription(*p), args)
            self._rets.put(future)
        except Exception as ex:
            print(ex)
        return future

    def submitDownloadTask(self, site, url, keyword, useremail):
        executor = self._domainExecutor[site]
        try:
            args = [self, site, url, keyword, useremail]
            future = executor.submit(
                lambda p: DownloadService.extractSearchSubscription(*p), args)
            self._rets.put(future)
        except Exception as ex:
            print(ex)
        return future

    def shutdown(self):
        self._thread._stop()

        return
