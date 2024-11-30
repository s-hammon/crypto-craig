-- +goose Up
CREATE INDEX listings_updated_at_idx ON listings (updated_at);

-- +goose Down
DROP INDEX listings_updated_at_idx;