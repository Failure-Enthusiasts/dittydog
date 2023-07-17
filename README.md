# dittydog

Requirements:
- npm
- python3
- vue
- git
- docker

## ECS Cluster ##

- https://ap-northeast-2.console.aws.amazon.com/ecs/v2/clusters/cahillsf-fg/services?region=ap-northeast-2#

Docs: 

- https://datadoghq.atlassian.net/wiki/spaces/TS/pages/328434517/AWS+Azure+GCP+Sandbox+Environments#AWS
- https://datadoghq.atlassian.net/wiki/spaces/SOE/pages/2786722152/AWS+Lambda+Parameter+Configuration?NO_SSR=1

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
## AWS ECS :

- upload the task definition
  ```
  aws-vault exec sandbox-account-admin -- aws ecs register-task-definition --endpoint-url https://ecs.ap-northeast-2.amazonaws.com --cli-input-json file://./aws/dd-task-def.json
  ```

- SSO version:
  ```
  aws-vault exec sso-sandbox-account-admin -- aws ecs register-task-definition  --region ap-northeast-2  --endpoint-url https://ecs.ap-northeast-2.amazonaws.com --cli-input-json file://./aws/dd-task-def.json 

  ```
