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
docker build -t bradleyjay/spotify-backend:aws_test_deploy .
docker tag bradleyjay/spotify-backend:aws_test_deploy bradleyjay/spotify-backend:aws_test_deploy

docker push bradleyjay/spotify-backend:aws_test_deploy
```
