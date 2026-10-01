-- Ce modèle agrège les données par jour
SELECT
    DISTINCT(date),
    city,
    AVG(temperature) AS avg_temp,
    MIN(temperature) AS min_temp,
    MAX(temperature) AS max_temp,
    AVG(cloud_cover) AS avg_cloud_cover,
    AVG(wind_speed) AS avg_wind_speed,
    MIN(wind_speed) AS min_wind_speed,
    MAX(wind_speed) AS max_wind_speed,
    AVG(wind_direction) AS avg_wind_direction,
    AVG(soil_temperature) AS avg_soil_temperature,
    MIN(soil_temperature) AS min_soil_temperature,
    MAX(soil_temperature) AS max_soil_temperature,
    AVG(soil_moisture) AS avg_soil_moisture
FROM {{ ref('stg_weather_raw') }}
GROUP BY date, city
ORDER BY date DESC