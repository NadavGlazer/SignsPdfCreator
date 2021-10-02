#FROM docker:latest
FROM python:3-alpine3.12
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libcurl bzip2-dev \
    py-cryptography \
    libjpeg-turbo-dev zlib-dev


RUN pip install --upgrade pandas

COPY ./templates /
WORKDIR / 
RUN pip install --index-url=https://pypi.python.org/simple/ -r requirements.txt

EXPOSE 5000


##ENTRYPOINT export FLASK_APP=app.py && flask run --host 0.0.0.0
ENTRYPOINT gunicorn --bind 0.0.0.0:5000 app:app
