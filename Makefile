include .env

up:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" up

down:
	@goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" down

.PHONY: up down