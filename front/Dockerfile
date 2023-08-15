# FROM node:lts-alpine as build-stage
# FROM node:14 as build-stage
FROM --platform=linux/amd64 node:14 as build-stage
WORKDIR /app
# COPY package*.json ./
COPY package.json ./
RUN npm install
RUN npm update
COPY . .
# CMD ["npm","run","serve"]
# CMD ["npm","run","build"]
RUN npm run build
# CMD ["sleep", "10000"]

# production stage
FROM --platform=linux/amd64 nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# COPY ./docker_init ./
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d
# RUN chmod +x ./docker_entrypoint.sh ./generate_env_config.sh
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# CMD ["/bin/sh", "docker_entrypoint.sh"]