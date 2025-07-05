#!/bin/bash

echo "Cleaning up Docker environment..."

# Stop and remove containers
echo "Stopping and removing containers..."
docker-compose -f ./docker-compose.yml down --rmi all --remove-orphans

# Remove all images (forced)
echo "Removing all Docker images..."
docker system prune -a -f

# Optional: Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Optional: Remove unused networks
echo "Removing unused networks..."
docker network prune -f

echo "Docker cleanup complete!"