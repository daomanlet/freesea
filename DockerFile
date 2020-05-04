FROM python:3
ENV PYTHONUNBUFFERED 1
RUN git clone https://daomanlet@github.com/daomanlet/freesea.git
WORKDIR freesea
RUN cd freesea
RUN pip install -r requirements.txt
COPY . /code/