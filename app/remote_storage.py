import mimetypes
import http.client
import logging
import os
from urllib.parse import urlsplit
import json
import urllib3
import seafileapi
from app.config import Config


class RemoteStorage():
    def upload(self, filename):
        pass
    
    def create_repository(self, repo_name):
        pass

class RemoteStorageWebDAV(RemoteStorage):

    _rootPath = None

    def __init__(self, repo_path):
        if repo_path is None:
            _rootPath = './video'
        else :    
            _rootPath = repo_path

    def create_repository(self, repo_name):
        cmd = 'mkdir ./video/'+repo_name
        os.system(cmd)
        return 

    def upload(self, filename):
        return

class RemoteStorageSeafile(RemoteStorage):

    # _client = seafileapi.connect(Config.REMOTE_STORAGE_URL,
    #                              Config.REMOTE_STORAGE_USER,
    #                              Config.REMOTE_STORAGE_PWD)

    _repo_id = None
    _token = None
    _http = urllib3.PoolManager()

    def create_repository(self, repo_name):
        url = Config.REMOTE_STORAGE_URL+'/api2/repos/'
        headers = {'Authorization': 'Token ' + self._token,
                   'Accept': 'application/json; indent=4'}
        fields = {'name': repo_name, 'desc': 'darksite added'}
        resp = self._http.request('POST', url, fields=fields, headers=headers)
        repo_id = json.loads(resp.data.decode('utf-8'))['repo_id']
        return repo_id

    def __init__(self, repo_name):
        url = Config.REMOTE_STORAGE_URL+'/api2/auth-token/'
        values = {'username': Config.REMOTE_STORAGE_USER,
                  'password': Config.REMOTE_STORAGE_PWD}
        resp = self._http.request('POST', url, fields=values)
        self._token = json.loads(resp.data.decode('utf-8'))['token']

        url = Config.REMOTE_STORAGE_URL+'/api2/repos/'
        resp = self._http.request(
            'GET', url, headers={"Authorization": 'Token ' + self._token})
        repos = json.loads(resp.data.decode('utf-8'))
        for i in repos:
            if i['name'] == repo_name:
                self._repo_id = i['id']
                break
        if self._repo_id is None:
            self._repo_id = self.create_repository(self._repo_id)
        return

    def _get_upload_link(self):
        url = Config.REMOTE_STORAGE_URL+'/api2/repos/'+self._repo_id+'/upload-link/'
        resp = self._http.request(
            'GET', url, headers={"Authorization": 'Token ' + self._token})
        return resp.data.decode('utf8').replace('"', '')

    def _post_multipart(self, scheme, host, port, selector, fields, files):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        content_type, body = self._encode_multipart_formdata(fields, files)
        if scheme and scheme.lower() == "http":
            h = http.client.HTTPConnection(host, port)
        else:
            h = http.client.HTTPSConnection(host, port)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        # print errcode, errmsg, headers
        return h.file.read()

    def _encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append(
                'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self._get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def upload(self, filename):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        #requests_log.propagate = True
        upload_link = self._get_upload_link()
        with open(filename, 'rb') as fp:
            binary_data = fp.read()
        base_name = os.path.basename(filename)
        fields = {
            'file': (base_name, binary_data, self._get_content_type(base_name)),
            'filename': base_name,
            'parent_dir': '/'

        }
        headers = {
            'Authorization': 'Token {token}'. format(token=self._token)
        }
        response = self._http.request("POST",
                                      # "http://httpbin.org/post",
                                      upload_link,
                                      fields=fields,
                                      headers=headers)
        return response
    # urlparts = urlsplit(upload_link[1:-1])

    # fields = [('parent_dir', '/'), ]
    # files = [('file', base_name, binary_data)]
    # self._post_multipart(urlparts.scheme, urlparts.netloc, urlparts.port,
    #                     urlparts.path, fields, files)
    # return
