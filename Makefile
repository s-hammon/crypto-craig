include .env

up:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" up

down:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" down

pretty:
	@ruff format && ruff check

test:
	@python3 -m unittest discover -s tests -v

fetch:
	@python3 main.py crawler job

bot:
	@python3 main.py craig

.PHONY: up down pretty test fetch bot