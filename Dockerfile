FROM ubuntu:latest

MAINTAINER Daemon-Shadowsocks-Links-Status Maintainers "1025123978@qq.com"

RUN apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
						ca-certificates \
						nginx \
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

RUN touch /usr/share/nginx/html/result.json && touch /usr/share/nginx/html/result.jsonp

ENTRYPOINT ["/usr/bin/supervisord"]
