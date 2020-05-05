FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y libmemcached-dev \
	zlib1g-dev \
	openssl \ 
	build-essential \
	libssl-dev \
	xvfb 
RUN git clone https://daomanlet:5Imaomao%40@github.com/daomanlet/freesea.git /opt/freesea
WORKDIR /opt/freesea
RUN cd /opt/ && wget https://downloads.wkhtmltopdf.org/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && tar -xvf ./wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && cd /opt/wkhtmltox && chown root:root bin/wkhtmltopdf && cp -r * /usr/
RUN pwd && pip install -r /opt/freesea/requirements.txt
