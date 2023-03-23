DROP TABLE IF EXISTS old_subscribers CASCADE;
DROP TABLE IF EXISTS subscribers CASCADE;
DROP TABLE IF EXISTS scheduler CASCADE;

CREATE TABLE scheduler (
	time TIME UNIQUE,
	count INTEGER DEFAULT(0)
);

CREATE TABLE subscribers (
	user_id INTEGER PRIMARY KEY,
	location VARCHAR(50),
	first_name VARCHAR(64),
	notifyTime TIME REFERENCES scheduler(time) ON DELETE RESTRICT ON UPDATE RESTRICT,
	paid_subscription DATE,
	discount INTEGER[][]
);

CREATE TABLE old_subscribers (
	user_id INTEGER UNIQUE,
	paid_subscription DATE
)