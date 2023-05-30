DELETE FROM paid_subscriptions;

INSERT INTO paid_subscriptions (name, label, price, period, description) VALUES (
    'one_month_sub',
    'Подписка на месяц',
    '{"total": 100}',
    '1 Month',
    'Месячная подписка на детальный прогноз погоды'
), (
    'one_year_month',
    'Годовая подписка',
    '{"base": 1000, "discount": 10}',
    '1 Year',
    'Годовая подписка на детальный прогноз погоды'
);
