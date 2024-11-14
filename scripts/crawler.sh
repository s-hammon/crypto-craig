#!/bin/bash

# template docker command
DOCKER_CMD="docker run -d --name crypto-crawler-bot -e CMC_PRO_API_KEY=$CMC_PRO_API_KEY -e TURSO_AUTH_TOKEN=$TURSO_AUTH_TOKEN -e DB_URL=$DB_URL sven210/crypto-craig"

TAG="latest"

if [ -n "$1" ]; then
    TAG="$1"
fi

# Check TAG format-- x.y.z format or 'latest'
if [[ ! "$TAG" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && [ "$TAG" != "latest" ]; then
    echo "Invalid tag format: $TAG"
    exit 1
fi

DOCKER_CMD="$DOCKER_CMD:$TAG crawler"

echo "Running $DOCKER_CMD"
eval $DOCKER_CMD