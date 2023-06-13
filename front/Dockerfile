# FROM node:lts-alpine as build-stage
FROM node:14 as build-stage
WORKDIR /app
# COPY package*.json ./
COPY package.json ./
RUN npm install
RUN npm update
COPY . .
CMD ["npm","run","serve"]