# 目的 翻墙访问youtube等视频网站比较慢，有些视频想下载看
## 可以下载视频网站
* youtube
* p站 不解释
# 使用方法
## 文件本地存储
* 申请一个digital ocean的droplet
* python3.6以上
* 安装相关系统包 apt-get update && apt-get install -y libmemcached-dev \
	zlib1g-dev \
	openssl \ 
	build-essential \
	libssl-dev \
	xvfb
* 创建freesea用户  useradd freesea
* mkdir /opt/freesea
* git clone https://github.com/daomanlet/freesea.git /opt/freesea
* cd /opt/freesea
* 创建virtual environment python3 -m venv /opt/freesea/py3
* 激活virtual environment source /opt/freesea/bin/active
* 安装依赖包 python -m pip install -r requirements.txt 
* app/config.py 修改邮件，webdav 配置
* uwsgi freesea.ini -H /opt/freesea/py3
## 使用seafile网盘
* 这里提供一个大家公用的网盘，你可以去注册使用，空间不大。放了不该放的内容会被管理员清掉
* 也可以按照下边的安装方法自己搭建一个网盘
## uBuntu使用imgkit需要安装特别的部分
* 参照imgkit[https://pypi.org/project/imgkit/]
* 其中静态库[https://github.com/jarrekk/imgkit/blob/master/travis/init.sh]也需要
* 特别加上这个 sudo apt-get install libssl1.0-dev 
## docker 
* https://hub.docker.com/repository/docker/rouynxia/freesea