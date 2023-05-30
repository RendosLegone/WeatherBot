DELETE FROM discounts;

INSERT INTO discounts (name, label, amount) VALUES (
    'global',
    'Летняя скидка',
    10);

INSERT INTO discounts (name, label, amount, trigger) VALUES (
    'inviting_1',
    'За приглашение реферала',
    10,
    '{"invite_users": 1}'
), (
    'inviting_5',
    'За приглашение 5 рефералов',
    20,
    '{"invite_users": 5}'
), (
    'inviting_with_purchase',
    'За покупку подписки рефералом',
    10,
    '{"invite_users": 1, "payment_subscription": 1}'
), (
    'invited',
    'Подписка по реферальной ссылке',
    10,
    '{"invited_from": true}'
);

INSERT INTO discounts (name, label, amount, limit_count, trigger) VALUES (
    'summer_promo',
    'Летний промокод',
    7,
    1000,
    '{"promo": "SUMMER_2023"}'
)
