FROM docker:latest
FROM python:3-alpine3.14
RUN apk add --no-cache --update \
	chromium-chromedriver \
	chromium \
	python3 python3-dev gcc \
	gfortran musl-dev g++ \
	libffi-dev openssl-dev \
	libxml2 libxml2-dev \
	libxslt libxslt-dev \
	libcurl bzip2-dev \
	py-cryptography \
	fontconfig ttf-dejavu \
	libjpeg-turbo-dev zlib-dev 

COPY . /Test
WORKDIR /Test/templates
 
RUN pip install -r requirements.txt
EXPOSE 5000


ENTRYPOINT gunicorn --bind 0.0.0.0:5000 app:app





