#!/bin/bash

# template docker command
DOCKER_CMD="docker run -d --name crypto-craig-bot -e DISCORD_TOKEN=$DISCORD_TOKEN -e TURSO_AUTH_TOKEN_DISCORD_CLIENT=$TURSO_AUTH_TOKEN_DISCORD_CLIENT -e DB_URL=$DB_URL sven210/crypto-craig"

TAG="latest"
DEBUG_MODE=""

if [ "$1" == "--debug" ]; then
    DEBUG_MODE="--debug"
elif [ -n "$1" ]; then
    TAG="$1"
fi

# Check TAG format-- x.y.z format or 'latest'
if [[ ! "$TAG" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && [ "$TAG" != "latest" ]; then
    echo "Invalid tag format: $TAG"
    exit 1
fi

if [ "$2" == "--debug" ]; then
    DEBUG_MODE="--debug"
fi

DOCKER_CMD="$DOCKER_CMD:$TAG craig $DEBUG_MODE"

echo "Running $DOCKER_CMD"
eval $DOCKER_CMD