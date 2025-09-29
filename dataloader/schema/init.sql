--- ENABLE PGVECTOR EXTENSION ---
CREATE EXTENSION if not exists vector;

--- MAKE APP SERVICE SCHEMAS ---

CREATE TABLE app_user
(
    user_id      UUID PRIMARY KEY,
    email        TEXT      NOT NULL,
    saltpassword TEXT      NOT NULL,
    name         TEXT      NOT NULL,
    region       TEXT,
    location     TEXT,
    created_at   TIMESTAMP NOT NULL
);