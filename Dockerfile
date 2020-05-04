FROM python:3
ENV PYTHONUNBUFFERED 1
RUN git clone https://daomanlet:5Imaomao%40@github.com/daomanlet/freesea.git
WORKDIR freesea
RUN cd freesea
RUN pip install -r requirements.txt