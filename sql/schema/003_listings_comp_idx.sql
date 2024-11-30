-- +goose Up
CREATE INDEX idx_coin_updated_at ON listings (coin, updated_at);

-- +goose Down
DROP INDEX idx_coin_updated_at;