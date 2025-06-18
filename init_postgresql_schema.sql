
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100),
    name VARCHAR(255),
    specs TEXT,
    category VARCHAR(100),
    manufacturer VARCHAR(100),
    year VARCHAR(10),
    date_in_use DATE,
    status VARCHAR(100),
    location VARCHAR(255),
    link TEXT,
    stage VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS maintenance_history (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    date DATE,
    content TEXT,
    performed_by VARCHAR(100),
    image_filename TEXT
);
