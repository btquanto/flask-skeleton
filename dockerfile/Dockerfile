FROM alpine
MAINTAINER Quan To <btquanto@gmail.com>

# basic flask environment
RUN apk add --no-cache bash git nginx py2-pip \
	&& pip2 install --upgrade pip

# application folder
ENV APP_DIR /src

# app dir
RUN mkdir ${APP_DIR} \
	&& chown -R nginx:nginx ${APP_DIR} \
	&& chmod 777 /run/ -R \
	&& chmod 777 /root/ -R
VOLUME [${APP_DIR}]
WORKDIR ${APP_DIR}

# expose web server port
# only http, for ssl use reverse proxy
EXPOSE 80

# copy config files into filesystem
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
