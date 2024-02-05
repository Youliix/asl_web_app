
-- Create table if not exists
CREATE TABLE IF NOT EXISTS my_table (
    id SERIAL PRIMARY KEY,
    label TEXT,
    image BYTEA,
    key_points JSONB
);
