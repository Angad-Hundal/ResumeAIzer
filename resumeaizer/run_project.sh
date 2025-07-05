#!/bin/bash

echo "Stopping any running containers..."
docker-compose -f ./docker-compose.yml down

echo "Building and starting containers..."
docker-compose -f ./docker-compose.yml up --build
