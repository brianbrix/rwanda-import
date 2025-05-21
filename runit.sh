#!/bin/bash

CONTAINER_NAME=$1
NETWORK_NAME=backend

if [ -z "$CONTAINER_NAME" ]; then
  echo "Usage: $0 <container-name>"
  exit 1
fi

# Check if the container is already in the network
if docker inspect "$CONTAINER_NAME" | grep -q "\"$NETWORK_NAME\":"; then
  echo "Container '$CONTAINER_NAME' is already connected to the '$NETWORK_NAME' network."
else
  echo "Connecting '$CONTAINER_NAME' to '$NETWORK_NAME'..."
  docker network connect "$NETWORK_NAME" "$CONTAINER_NAME"
  echo "Done."
fi

docker-compose build --no-cache
docker-compose up -d
