#!/bin/bash

# Build the Docker image with tag from CLI 
# throw error if $1 is not provided
if [ -z "$1" ]
then
    echo "Usage: $0 <tag>"
    exit 1
fi

# Build the Docker image with the provided tag
docker build -t sven210/crypto-craig:$1 -t sven210/crypto-craig:latest .