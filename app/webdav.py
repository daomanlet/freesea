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
    
    def getRepositoryID(self, repo_name):
        url = Config.REMOTE_STORAGE_URL+'/api2/repos/'
        resp = self._http.request(
            'GET', url, headers={"Authorization": 'Token ' + self._token})
        repos = json.loads(resp.data.decode('utf-8'))
        repo_id = None
        for i in repos:
            if i['name'] == repo_name:
                repo_id = i['id']
                break
        return repo_id

    def shareFolder(self, repo_name, email, permission='r'):
        repo_id = self.getRepositoryID(repo_name)
        if repo_id is None:
            repo_id = self.create_repository(repo_name)
        url = Config.REMOTE_STORAGE_URL+'/api2/shared-repos/'+repo_id+'/'
        param = '?share_type=personal&user='+email+'&permission='+permission
        url = url + param
        resp = self._http.request(
            'PUT', url, headers={"Authorization": 'Token ' + self._token})            
        ret = json.loads(resp.data.decode('utf-8'))
        if ret == "success":
            return True
        return False

    def create_repository(self, repo_name):
        url = Config.REMOTE_STORAGE_URL+'/api2/repos/'
        headers = {'Authorization': 'Token ' + self._token,
                   'Accept': 'application/json; indent=4'}
        fields = {'name': repo_name, 'desc': 'darksite added'}
        resp = self._http.request('POST', url, fields=fields, headers=headers)
        repo_id = json.loads(resp.data.decode('utf-8'))['repo_id']
        return repo_id