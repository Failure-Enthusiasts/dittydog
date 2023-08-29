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

- create the target group:
  ```
  TARGET_GROUP=$(aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-target-group --name fargate-target --protocol HTTP --port 80 --vpc-id $DEFAULT_VPC_ID --target-type ip --region ap-northeast-2 --query "TargetGroups[0].TargetGroupArn" | tr -d '"')
  ```
  - maybe we need to pipe to `tr -d '"'` in order to remove the double quotes for the `create-service` command to evaluate

- create the load balancer:
  ```
  LOAD_BALANCER=$(aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-load-balancer --name dittydog-lb --subnets=$DBLQUOTE_SPACE_SEP_PRIVATE_SUBNETS --security-groups $DITTYDOG_LB_SG_2 --scheme internet-facing --region ap-northeast-2 --query "LoadBalancers[0].LoadBalancerArn" | tr -d '"')
  ```
  - need to wait until the load balancer is provisioned before proceeding: `aws elbv2 --region ap-northeast-2 describe-load-balancers --load-balancer-arns ${LOAD_BALANCER}`

- create the listener:
  ```
  aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-listener --load-balancer-arn=$LOAD_BALANCER --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP --region ap-northeast-2
  ```

- launch the service:
  ```
  aws-vault exec sso-sandbox-account-admin -- aws ecs create-service --cluster cahillsf-fg --service-name dittydog --task-definition dittydog:18 --enable-execute-command --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$COMMA_SEP_PRIVATE_SUBNETS],securityGroups=[$DITTYDOG_LB_SG_1],assignPublicIp=ENABLED}" --load-balancers '[{"targetGroupArn": "'"$TARGET_GROUP"'", "containerName": "dittydog-frontend","containerPort": 80}]' --region ap-northeast-2
  ```

### To run the startup script:
1) Source env vars (Brad's machine? `source aws/.dittydog_env_vars.sh`)
2) Ensure the `aws/dd-task-def.json` includes the right image version:

```

"containerDefinitions": [
    {
      "name": "spotify-backend",
      "image": "public.ecr.aws/b1o7r7e0/be-dittydog:8-14-23",
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080
        }
      ],

```
3) Ensure the `aws/dd-task-def.json` has the correct `taskRoleArn` and `executionRoleArn` values (i.e., not blank)

4) Login to [AWS](https://d-906757b57c.awsapps.com/start#/)

5) Run the script
- make the shell file executable `chmod 755 launch-ecs-service.sh`
- `source ./launch-ecs-service.sh`

6) While everything is provisioning, go find:
   1) The load balancer. Search Load Balancers in the AWS search bar, click on "EC2 feature", look for *dittydog-lb*.
   2) Check the cluster for the deployed containers: [cahillsf-fg](https://ap-northeast-2.console.aws.amazon.com/ecs/v2/clusters/cahillsf-fg/services?region=ap-northeast-2)

7) Log into the app.
   1) Hop over to the load balancer again. Copy the DNS URL, paste that into your browser.
