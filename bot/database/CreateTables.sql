DROP TABLE IF EXISTS old_subscribers CASCADE;
DROP TABLE IF EXISTS subscribers CASCADE;
DROP TABLE IF EXISTS scheduler CASCADE;
DROP TABLE IF EXISTS discounts CASCADE;

CREATE TABLE scheduler (
	time TIME UNIQUE,
	count INTEGER DEFAULT(0)
);

CREATE TABLE subscribers (
	user_id INTEGER NOT NULL PRIMARY KEY UNIQUE,
	location VARCHAR(50) NOT NULL,
	username VARCHAR(64) NOT NULL,
	notify_time TIME NOT NULL REFERENCES scheduler(time) ON DELETE RESTRICT ON UPDATE RESTRICT,
	paid_subscription DATE,
	discounts VARCHAR[] REFERENCES discounts(name) ON DELETE RESTRICT ON UPDATE RESTRICT,
	invited_from REFERENCES subscribers(user_id) INTEGER
);

CREATE TABLE old_subscribers (
	user_id INTEGER PRIMARY KEY UNIQUE,
	paid_subscription DATE
);

CREATE TABLE discounts (
    name VARCHAR,
    label VARCHAR,
    amount INTEGER(100) NOT NULL,
    limit_count INTEGER,
    summed_up boolean DEFAULT(TRUE),
    trigger jsonb
)