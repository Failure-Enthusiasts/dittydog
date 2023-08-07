FROM --platform=linux/amd64 node:14
WORKDIR /usr/src/app
COPY package*.json server.js ./
RUN npm install
EXPOSE 4001
CMD ["npm" , "start"]