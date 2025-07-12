#!/bin/bash

# Load .env variables into current shell
if [ -f ./.env ]; then
    export $(grep -v '^#' ./.env | xargs)
    echo "Loaded environment variables from .env file"
else
    echo "Warning: No .env file found"
fi

echo "Stopping any running containers..."
docker-compose -f ./docker-compose.yml down

echo "Building and starting containers..."
docker-compose -f ./docker-compose.yml up --build