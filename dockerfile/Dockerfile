FROM alpine
MAINTAINER Quan To <btquanto@gmail.com>

# basic flask environment
RUN apk add --no-cache bash git py2-pip py-virtualenv alpine-sdk build-base python-dev libffi-dev \
	&& pip2 install --upgrade pip \
	&& pip2 install gunicorn==19.6.0

# application folder
ENV APP_DIR /src

# app dir
RUN mkdir ${APP_DIR}
WORKDIR ${APP_DIR}

# expose web server port
# only http, for ssl use reverse proxy
EXPOSE 8000
