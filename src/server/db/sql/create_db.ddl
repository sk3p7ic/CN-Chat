-- create_db.ddl :: Server Database Creation Script
-- This file is used to create the database used in CN-Chat's server.

-- app_users table :: stores the data about the users of the database
CREATE TABLE IF NOT EXISTS app_users(
    user_id     INT     NOT NULL UNIQUE,
    username    TEXT    NOT NULL,
    password    TEXT    NOT NULL,
    token       TEXT    NOT NULL
);

-- app_servers table :: stores the data about the servers in the database
CREATE TABLE IF NOT EXISTS app_servers(
    server_id           INT         NOT NULL,
    server_name         TEXT        NOT NULL,
    -- NOTE: boolean will be converted to an int of either 0 or 1 (false/true)
    --       due to the way that sqlite is designed
    server_is_public    BOOLEAN     NOT NULL
);

-- private_server_members table :: stores the members of private servers
CREATE TABLE IF NOT EXISTS private_server_members(
    private_server_id   INT,
    first_user_id       INT,
    second_user_id      INT,
    FOREIGN KEY(private_server_id) REFERENCES app_servers(server_id),
    FOREIGN KEY(first_user_id) REFERENCES app_users(user_id),
    FOREIGN KEY(second_user_id) REFERENCES app_users(user_id)
);

-- server_members table :: stores the members of various servers
CREATE TABLE IF NOT EXISTS server_members(
    public_server_id    INT,
    public_user_id      INT,
    FOREIGN KEY(public_server_id) REFERENCES app_servers(server_id),
    FOREIGN KEY(public_user_id) REFERENCES app_users(user_id)
);

-- server_messages table :: stores the messages that are sent in each server
CREATE TABLE IF NOT EXISTS server_messages(
    message_id          INT     PRIMARY KEY ASC,
    server_id           INT     NOT NULL,
    message_text        TEXT,
    message_attachment  BLOB,
    FOREIGN KEY(server_id) REFERENCES app_servers(server_id)
);
