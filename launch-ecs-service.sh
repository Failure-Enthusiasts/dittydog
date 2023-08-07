#!/bin/bash
TARGET_GROUP=$(aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-target-group --name fargate-target --protocol HTTP --port 80 --vpc-id $DEFAULT_VPC_ID --target-type ip --region ap-northeast-2 --query "TargetGroups[0].TargetGroupArn" | tr -d '"')
LOAD_BALANCER=$(aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-load-balancer --name dittydog-lb --subnets=$DBLQUOTE_SPACE_SEP_PRIVATE_SUBNETS --security-groups $DITTYDOG_LB_SG_2 --scheme internet-facing --region ap-northeast-2 --query "LoadBalancers[0].LoadBalancerArn" | tr -d '"')

LB_READY=false
while [[ "$LB_READY" = false ]]
do
  echo $LB_READY
  sleep 10
  STATE=$(aws-vault exec sso-sandbox-account-admin -- aws elbv2 --region ap-northeast-2 describe-load-balancers --load-balancer-arns ${LOAD_BALANCER} --query "LoadBalancers[0].State.Code" | tr -d '"')
  echo $STATE
  if [[ "$STATE" = "active" ]]
  then
    echo "state is active, setting LB_READY=true"
    LB_READY=true
  fi
  echo $LB_READY
done


aws-vault exec sso-sandbox-account-admin -- aws elbv2 create-listener --load-balancer-arn=$LOAD_BALANCER --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP --region ap-northeast-2

aws-vault exec sso-sandbox-account-admin -- aws ecs create-service --cluster cahillsf-fg --service-name dittydog --task-definition dittydog:18 --enable-execute-command --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$COMMA_SEP_PRIVATE_SUBNETS],securityGroups=[$DITTYDOG_LB_SG_1],assignPublicIp=ENABLED}" --load-balancers '[{"targetGroupArn": "'"$TARGET_GROUP"'", "containerName": "dittydog-frontend","containerPort": 80}]' --region ap-northeast-2