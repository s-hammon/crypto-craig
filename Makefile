include .env

up:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" up

down:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" down

pretty:
	@ruff format && ruff check

test:
	@python -m unittest discover -s tests -v

.PHONY: up down pretty test