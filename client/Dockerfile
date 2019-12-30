FROM node:12-alpine

WORKDIR /client

COPY package.json /client/package.json
RUN npm install

CMD [ "npm", "start" ]

EXPOSE 3000
