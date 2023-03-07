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

