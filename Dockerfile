FROM python:3.7

COPY . /raven
WORKDIR /raven

RUN apt-get update && \
  make init

CMD make start-server

EXPOSE 3001
