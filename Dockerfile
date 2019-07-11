FROM python:3.7

COPY . /raven
WORKDIR /raven

RUN apt-get update && \
  curl -sL https://deb.nodesource.com/setup_10.x | bash && \
  apt-get install nodejs && \
  npm i -g nodemon && \
  make init

CMD make start-server

EXPOSE 3001
