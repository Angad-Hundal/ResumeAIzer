#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Kubernetes deployment for ResumeAIzer...${NC}"

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --driver=docker
fi

# Configure Docker to use Minikube's daemon
echo -e "${YELLOW}Configuring Docker...${NC}"
eval $(minikube -p minikube docker-env)

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace resumeaizer --dry-run=client -o yaml | kubectl apply -f -

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
docker build -t resumeaizer-backend:latest ../backend
docker build -t resumeaizer-frontend:latest ../frontend

# Apply configurations
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
kubectl apply -f . -n resumeaizer

# Wait for pods
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=backend -n resumeaizer --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n resumeaizer --timeout=120s

# Get external URLs
echo -e "${YELLOW}Getting service URLs...${NC}"
minikube service frontend-service -n resumeaizer --url
minikube service backend-service -n resumeaizer --url

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Frontend will communicate with backend using: http://backend-service:8000${NC}"