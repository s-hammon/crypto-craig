#!/bin/bash

if [ -f .env ]; then
    set -a
    . .env
    set +a
else
    ./scripts/create-env-file.sh
    echo ".env file created. Please fill in the necessary values."
fi

if ! command -v goose &> /dev/null
then
    curl -fsSL https://raw.githubusercontent.com/pressly/goose/master/install.sh | \
        GOOSE_INSTALL=$HOME/.goose sh -s v3.22.1
fi
