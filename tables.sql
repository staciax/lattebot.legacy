CREATE SCHEMA valorant

CREATE TABLE IF NOT EXISTS valorant.users
(
    user_id bigint NOT NULL,
    puuid VARCHAR(40),
    player_name VARCHAR(25),
    region text VARCHAR(5),
    expiry_token integer,
    headers VARCHAR(4000),
    cookies VARCHAR(4000),
    notify_mode character VARCHAR(10),
    guild_id bigint
)

CREATE TABLE IF NOT EXISTS valorant.notifys
(
    user_id bigint NOT NULL,
    uuid VARCHAR(40),
    guild_id bigint
)

CREATE SCHEMA admin

CREATE TABLE IF NOT EXISTS admin.blacklist
(
    snowflake_id BIGINT PRIMARY KEY,
    REASON VARCHAR(4000),
    timestamp TIMESTAMP
;