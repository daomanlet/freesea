from app import (app, db)
from sites.downloader import DownloadService

if __name__ == '__main__':
    db.create_all()
    _downloadSrv = DownloadService()
    app.run(threaded=True,
            port=7777)
    _downloadSrv.shutdown()