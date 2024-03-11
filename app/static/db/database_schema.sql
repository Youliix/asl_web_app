DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS keypoints;
DROP TABLE IF EXISTS posts;

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    image BYTEA
);

CREATE TABLE IF NOT EXISTS keypoints (
    id SERIAL PRIMARY KEY,
    label TEXT,
    keypoints float[],
    image_id INTEGER REFERENCES images(id)
);
