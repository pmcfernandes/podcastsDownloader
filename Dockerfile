FROM alpine
LABEL maintainer="pmcfernandes"
LABEL version="1.0"

USER 0

RUN apk upgrade --available
RUN apk add --update --no-cache \
	python3 \
	bash \
	curl && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN mkdir -p /config
RUN mkdir -p /podcasts

WORKDIR /usr/src/app

COPY crontab /etc/cron.d/crontab
COPY pod.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN crontab /etc/cron.d/crontab
CMD ["crond", "-f"]
