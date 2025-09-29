--- ENABLE PGVECTOR EXTENSION ---
CREATE EXTENSION if not exists vector;

--- MAKE APP SERVICE SCHEMAS ---

CREATE TABLE app_user
(
    user_id      UUID PRIMARY KEY,
    email        TEXT      NOT NULL,
    name         TEXT,
    saltpassword TEXT      NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    access_token TEXT,
    refresh_token TEXT
);

CREATE TABLE knowledge
(
    knowledge_id UUID PRIMARY KEY,
    creator_id  UUID REFERENCES app_user,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL
);

CREATE TABLE email
(
    email_id UUID PRIMARY KEY,
    user_id UUID REFERENCES app_user,
    from_sender TEXT,
    email_subject TEXT,
    email_status TEXT,
    email_timestamp TEXT,
    full_content TEXT,
    summary TEXT,
    draft_response TEXT
);

CREATE TABLE task
(
    task_id UUID PRIMARY KEY,
    user_id UUID REFERENCES app_user,
    title TEXT,
    task_description TEXT,
    task_priority TEXT,
    due_date TIMESTAMP,
    completed TEXT,
    email_id UUID REFERENCES email,
    created_at TIMESTAMP
);

CREATE TABLE invoice
(
    invoice_id UUID PRIMARY KEY,
    creator_id UUID REFERENCES app_user,
    full_name TEXT,
    phone_number TEXT,
    consumer_address TEXT,
    item_name TEXT,
    item_cost REAL
)