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

# Point shell to minikube's docker-daemon
echo -e "${YELLOW}Configuring Docker to use Minikube's Docker daemon...${NC}"
eval $(minikube -p minikube docker-env)

# Create namespace if it doesn't exist
if ! kubectl get namespace resumeaizer &> /dev/null; then
    echo -e "${YELLOW}Creating resumeaizer namespace...${NC}"
    kubectl create namespace resumeaizer
fi

# Build Docker images directly in Minikube's context
echo -e "${YELLOW}Building Docker images in Minikube's context...${NC}"
cd ../backend && docker build -t resumeaizer-backend:latest . && cd ../k8s
cd ../frontend && docker build -t resumeaizer-frontend:latest . && cd ../k8s

# Apply Kubernetes configurations
echo -e "${YELLOW}Applying Kubernetes configurations...${NC}"
kubectl apply -f configmap.yaml -n resumeaizer
kubectl apply -f backend-deployment.yaml -n resumeaizer
kubectl apply -f frontend-deployment.yaml -n resumeaizer

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=backend -n resumeaizer --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n resumeaizer --timeout=120s

# Start tunnel for services in background
echo -e "${YELLOW}Starting Minikube tunnel...${NC}"
minikube tunnel > /dev/null 2>&1 &
TUNNEL_PID=$!

# Wait a moment for tunnel to establish
sleep 5

# Get service URLs
echo -e "${YELLOW}Getting service URLs...${NC}"
FRONTEND_URL=$(minikube service frontend-service -n resumeaizer --url)
BACKEND_URL=$(minikube service backend-service -n resumeaizer --url)

echo -e "${GREEN}Frontend is available at: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend is available at: ${BACKEND_URL}${NC}"

# Add trap to clean up tunnel on script exit
trap "kill $TUNNEL_PID" EXIT

echo -e "${GREEN}ResumeAIzer has been successfully deployed!${NC}"
echo -e "${GREEN}You can check the status of your pods with: kubectl get pods -n resumeaizer${NC}"
