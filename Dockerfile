FROM python:3.9-alpine
LABEL maintainer="pmcfernandes"
LABEL version="1.0"

USER 0

RUN mkdir -p /config
RUN mkdir -p /podcasts

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY crontab /etc/cron.d/crontab
COPY . .

RUN crontab /etc/cron.d/crontab
CMD ["cron", "-f"]