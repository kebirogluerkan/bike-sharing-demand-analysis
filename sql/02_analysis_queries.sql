-- Hourly demand
SELECT
    rental_hour,
    ROUND(AVG(total_rentals), 1) AS avg_rentals,
    ROUND(AVG(casual_rentals), 1) AS avg_casual,
    ROUND(AVG(registered_rentals), 1) AS avg_registered
FROM bike_rentals_hourly
GROUP BY rental_hour
ORDER BY rental_hour;

-- Working day comparison
SELECT
    CASE WHEN workingday_flag = 1 THEN 'Working Day' ELSE 'Weekend/Holiday' END AS day_type,
    SUM(total_rentals) AS total_rentals,
    ROUND(AVG(total_rentals), 1) AS avg_hourly_rentals,
    ROUND(100 * SUM(registered_rentals) / SUM(total_rentals), 1) AS registered_share_pct
FROM bike_rentals_hourly
GROUP BY workingday_flag;

-- Season and weather analysis
SELECT
    season_id,
    weather_id,
    COUNT(*) AS observations,
    ROUND(AVG(total_rentals), 1) AS avg_hourly_rentals
FROM bike_rentals_hourly
GROUP BY season_id, weather_id
ORDER BY season_id, weather_id;

-- Peak time windows
SELECT *
FROM (
    SELECT
        rental_hour,
        ROUND(AVG(total_rentals), 1) AS avg_rentals
    FROM bike_rentals_hourly
    GROUP BY rental_hour
    ORDER BY avg_rentals DESC
)
WHERE ROWNUM <= 5;
