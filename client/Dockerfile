FROM node:10-alpine

COPY . /client
WORKDIR /client

RUN npm install

CMD [ "npm", "start" ]

EXPOSE 3000
