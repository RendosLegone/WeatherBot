DROP TABLE IF EXISTS old_subscribers CASCADE;
DROP TABLE IF EXISTS subscribers CASCADE;
DROP TABLE IF EXISTS scheduler CASCADE;
DROP TABLE IF EXISTS discounts CASCADE;
DROP TABLE IF EXISTS paid_subscriptions CASCADE;
DROP TABLE IF EXISTS purchase_receipts CASCADE;

CREATE TABLE scheduler (
	time TIME UNIQUE,
	count INTEGER DEFAULT(0)
);

CREATE TABLE discounts (
    name VARCHAR UNIQUE,
    label VARCHAR,
    amount INTEGER NOT NULL,
    limit_count INTEGER,
    summed_up boolean DEFAULT(TRUE),
    trigger jsonb
);

CREATE TABLE subscribers (
	user_id INTEGER NOT NULL PRIMARY KEY UNIQUE,
	location VARCHAR(50) NOT NULL,
	username VARCHAR(64) NOT NULL,
	notify_time TIME NOT NULL REFERENCES scheduler(time) ON DELETE RESTRICT ON UPDATE RESTRICT,
	paid_subscription_id VARCHAR UNIQUE,
	discounts VARCHAR[],
	invited_from INTEGER REFERENCES subscribers(user_id)
);

CREATE TABLE old_subscribers (
	user_id INTEGER PRIMARY KEY UNIQUE,
	paid_subscription jsonb
);

CREATE TABLE paid_subscriptions (
    name VARCHAR NOT NULL UNIQUE,
    label VARCHAR NOT NULL,
    price jsonb NOT NULL,
    period INTERVAL NOT NULL,
    description VARCHAR,
    photo_url VARCHAR
);

CREATE TABLE purchase_receipts (
    subscription_name VARCHAR NOT NULL,
    currency VARCHAR NOT NULL,
    total_amount INTEGER NOT NULL,
    telegram_purchase_id VARCHAR NOT NULL UNIQUE,
    provider_purchase_id VARCHAR NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    shipping_option_id VARCHAR,
    order_info jsonb,
    date_time TIMESTAMP NOT NULL
)
