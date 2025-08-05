#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# AWS Configuration
AWS_REGION="us-east-1"  # Change this to your preferred region
ECR_REPO_FRONTEND="resumeaizer-frontend"
ECR_REPO_BACKEND="resumeaizer-backend"
ECS_CLUSTER="resumeaizer-cluster"
ECS_SERVICE_FRONTEND="resumeaizer-frontend-service"
ECS_SERVICE_BACKEND="resumeaizer-backend-service"

echo -e "${YELLOW}Starting AWS deployment for ResumeAIzer...${NC}"

# Login to AWS ECR
echo -e "${YELLOW}Logging into AWS ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repositories if they don't exist
echo -e "${YELLOW}Creating ECR repositories...${NC}"
aws ecr create-repository --repository-name $ECR_REPO_FRONTEND --region $AWS_REGION || true
aws ecr create-repository --repository-name $ECR_REPO_BACKEND --region $AWS_REGION || true

# Build and push Docker images
echo -e "${YELLOW}Building and pushing Docker images...${NC}"
docker build -t $ECR_REPO_FRONTEND ../frontend
docker tag $ECR_REPO_FRONTEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest

docker build -t $ECR_REPO_BACKEND ../backend
docker tag $ECR_REPO_BACKEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BACKEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BACKEND:latest

# Deploy ECS resources
echo -e "${YELLOW}Deploying ECS resources...${NC}"
aws cloudformation deploy \
    --template-file cloudformation.yaml \
    --stack-name resumeaizer \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        FrontendImage=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest \
        BackendImage=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BACKEND:latest

# Get the ALB DNS name
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name resumeaizer \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Your application is available at: http://$ALB_DNS${NC}"
