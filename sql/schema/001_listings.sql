-- +goose Up
CREATE TABLE listings (
    id TEXT PRIMARY KEY,
    updated_at TEXT,
    coin TEXT,
    supply REAL,
    price REAL,
    volume_24h REAL,
    percent_1h REAL,
    percent_24h REAL
);

-- +goose Down
DROP TABLE listings;