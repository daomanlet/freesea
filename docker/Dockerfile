FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y libmemcached-dev zlib1g-dev && apt-get install -y openssl build-essential xorg libssl-dev xvfb 
RUN git clone https://daomanlet:5Imaomao%40@github.com/daomanlet/freesea.git /opt/freesea
WORKDIR /opt/freesea
RUN cd /opt/
RUN wget https://downloads.wkhtmltopdf.org/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cd /opt/wkhtmltox && sudo chown root:root bin/wkhtmltopdf && sudo cp -r * /usr/
RUN pwd && pip install -r /opt/freesea/requirements.txt
