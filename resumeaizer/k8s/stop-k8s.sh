#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping ResumeAIzer Kubernetes deployment...${NC}"

# Check if namespace exists
if kubectl get namespace resumeaizer &> /dev/null; then
    # Delete all resources in the namespace
    echo -e "${YELLOW}Removing all deployments and services...${NC}"
    kubectl delete -f frontend-deployment.yaml -n resumeaizer
    kubectl delete -f backend-deployment.yaml -n resumeaizer
    kubectl delete -f configmap.yaml -n resumeaizer
    
    # Delete the namespace
    echo -e "${YELLOW}Deleting resumeaizer namespace...${NC}"
    kubectl delete namespace resumeaizer
    
    echo -e "${GREEN}ResumeAIzer has been successfully stopped and cleaned up!${NC}"
else
    echo -e "${RED}ResumeAIzer namespace not found. Nothing to clean up.${NC}"
fi

# Ask if user wants to stop Minikube
read -p "Do you want to stop Minikube? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Stopping Minikube...${NC}"
    minikube stop
    echo -e "${GREEN}Minikube stopped successfully!${NC}"
fi
