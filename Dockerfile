FROM debian:jessie

MAINTAINER Daemon-Shadowsocks-Links-Status Maintainers "TOSANDORIN@Yahoo.com"

ENV NGINX_VERSION 1.11.3-1~jessie

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
						ca-certificates \
						nginx=${NGINX_VERSION} \
						nginx-module-xslt \
						nginx-module-geoip \
						nginx-module-image-filter \
						nginx-module-perl \
						nginx-module-njs \
						gettext-base \
						python3 \
						python3-pip \
						m2crypto \
						gcc \
						build-essential \
						supervisor \
						cron \
						wget \
						vim \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip3 install shadowsocks pysocks

RUN wget https://download.libsodium.org/libsodium/releases/LATEST.tar.gz \ 
	&& tar zxf LATEST.tar.gz \
	&& cd libsodium* \
	&& ./configure \
	&& make && make install \
	&& echo /usr/local/lib > /etc/ld.so.conf.d/usr_local_lib.conf \
	&& ldconfig

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

COPY nginx.conf /etc/nginx/nginx.conf

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY cron-tasks /etc/cron.d/cron-tasks

COPY app /app

WORKDIR /app

RUN chmod 0600 /etc/cron.d/cron-tasks

RUN touch /var/log/cron.log

RUN touch /usr/share/nginx/html/result.json

ENTRYPOINT ["/usr/bin/supervisord"]
