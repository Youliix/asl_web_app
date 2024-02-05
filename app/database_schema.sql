-- DROP TABLE IF EXISTS posts;

-- Create table if not exists
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    label TEXT,
    image BYTEA,
    key_points float[]
);
