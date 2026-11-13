CREATE TABLE bike_rentals_hourly (
    record_id          NUMBER PRIMARY KEY,
    rental_date        DATE NOT NULL,
    season_id          NUMBER(1),
    year_id            NUMBER(1),
    month_id           NUMBER(2),
    rental_hour        NUMBER(2),
    holiday_flag       NUMBER(1),
    weekday_id         NUMBER(1),
    workingday_flag    NUMBER(1),
    weather_id         NUMBER(1),
    temperature_norm   NUMBER(8,4),
    feels_like_norm    NUMBER(8,4),
    humidity_norm      NUMBER(8,4),
    windspeed_norm     NUMBER(8,4),
    casual_rentals     NUMBER,
    registered_rentals NUMBER,
    total_rentals      NUMBER
);
