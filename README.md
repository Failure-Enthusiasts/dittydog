# dittydog

Requirements:
- npm
- python3
- vue
- git
- docker


## New hotness:

```
cd back
./the_startup_script_of_the_century.sh


```

## Old way:
Spin up backend: `docker-compose up --build`  
Spin up frontend:
`npm install`
`npm run serve`

Spin up websocket: from `server` dir
`npm install`
`npm start`


Socket ref: https://www.digitalocean.com/community/tutorials/vuejs-vue-socketio

### How to push up a docker image

```
# DOCKER HUB

docker login
docker build -t bradleyjay/spotify-backend:7-10-23 .
docker tag bradleyjay/spotify-backend:7-10-23 bradleyjay/spotify-backend:7-10-23
docker push bradleyjay/spotify-backend:7-10-23

# AWS ECR

aws-vault exec sso-sandbox-account-admin -- aws  ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/b1o7r7e0

docker build -t be-dittydog:7-10-23 .
docker tag be-dittydog:7-10-23 public.ecr.aws/b1o7r7e0/be-dittydog:7-10-23
docker push public.ecr.aws/b1o7r7e0/be-dittydog:7-10-23

(do once for each of: be, fe, mw)

```
