from app.config import Config
from app.models import User
from urllib.parse import urlsplit
import json
import urllib3

class WebDAV():

    _token = None
    _http = urllib3.PoolManager()

    def __init__(self):
        url = Config.REMOTE_STORAGE_URL+'/api2/auth-token/'
        values = {'username': Config.REMOTE_STORAGE_USER,
                  'password': Config.REMOTE_STORAGE_PWD}
        resp = self._http.request('POST', url, fields=values)
        self._token = json.loads(resp.data.decode('utf-8'))['token']        

    def addUser(self, email, password):
        url = Config.REMOTE_STORAGE_URL+'/api2/accounts/'+email+'/'
        headers = {'Authorization': 'Token ' + self._token,
                   'Accept': 'application/json; indent=4'}
        fields = {'password': password }
        resp = self._http.request('PUT', url, fields=fields, headers=headers)
        if resp.status == 201:
            return True
        else :
            return False
    
    def shareFolder(self, name):
        return