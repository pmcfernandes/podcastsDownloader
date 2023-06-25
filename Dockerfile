FROM alpine
LABEL maintainer="pmcfernandes"
LABEL version="1.0"

USER 0
EXPOSE 80

RUN apk upgrade --available
RUN apk add --update --no-cache python3 py3-pip py3-virtualenv bash curl nodejs npm \
    && ln -sf python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip

RUN mkdir -p /podcasts
RUN mkdir -p /config && mkdir -p /usr/src/app

WORKDIR /config
COPY config/podcasts.db ./

WORKDIR /usr/src/app
COPY crontab /etc/cron.d/crontabs
RUN crontab /etc/cron.d/crontabs

COPY requirements.txt ./
COPY pod.py ./
COPY server/ ./
RUN rm pod.bat

RUN virtualenv ./venv
RUN source ./venv/bin/activate && pip install --no-cache-dir -r requirements.txt
RUN npm install

CMD ["/bin/bash", "-c", "crond -f"]
ENTRYPOINT ["/bin/bash", "-c", "export NODE_ENV=production && node app.js"]

