-- Ce modèle agrège les données par jour
SELECT
    date,
    city,
    AVG(temperature) AS avg_temp,
    MIN(temperature) AS min_temp,
    MAX(temperature) AS max_temp
FROM {{ ref('stg_weather_raw') }}
GROUP BY date, city
ORDER BY date DESC