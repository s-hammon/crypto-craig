#!/bin/bash

# Install Ruff, a Python linter
curl -LsSf https://astral.sh/ruff/install.sh | sh

# Install Goose, a database migration tool
curl -fsSL https://raw.githubusercontent.com/pressly/goose/master/install.sh | \
    GOOSE_INSTALL=$HOME/.goose sh -s v3.22.1

if [ ! -f .env ]; then
    ./scripts/create-env-file.sh
    echo ".env file created. Please fill in the necessary values."
fi