-- Ce modèle "staging" prend les données brutes et les prépare
SELECT
    timestamp,
    temperature,
    humidity,
    precipitation,
    cloud_cover,
    wind_speed,
    wind_direction,
    soil_temperature,
    soil_moisture,
    is_day,
    city,
    DATE(timestamp) AS date
FROM weather_raw