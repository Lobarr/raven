FROM node:12-alpine

COPY . /client
WORKDIR /client

RUN npm ci

CMD [ "npm", "start" ]

EXPOSE 3000
