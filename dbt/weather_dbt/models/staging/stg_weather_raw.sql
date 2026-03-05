-- Ce modèle "staging" prend les données brutes et les prépare
SELECT
    timestamp,
    temperature,
    city,
    DATE(timestamp) AS date
FROM weather_raw