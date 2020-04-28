from app.remote_storage import RemoteStorage
import sys

def testRemoteStorage():
    storage = RemoteStorage("北京")
    #storage.upload("C:\\Users\\xia_z\\src\\youtube_crawler\\darksite\\video\\北京\\北京姐们探讨如何更爽的操逼.jpg")
    #storage.upload("app.db")
    print(sys.getdefaultencoding())
    s = "./video/北京.txt"
    ret = storage.upload(s)
    print(ret.status)

if __name__ == '__main__':

    testRemoteStorage()
    
