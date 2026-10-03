import openmeteo_requests
import psycopg2
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

API_URL = "https://archive-api.open-meteo.com/v1/archive"

LATITUDE = 43.61
LONGITUDE = 3.87
HOURLY = ["temperature_2m",
          "relative_humidity_2m",
          "precipitation",
          "cloud_cover",
          "wind_speed_10m",
          "wind_direction_10m",
          "soil_temperature_0_to_7cm",
          "soil_moisture_0_to_7cm",
          "is_day"]
CITY = "Montpellier"

DB_HOST = "weather_postgres"
DB_PORT = 5432
DB_NAME = "weather_db"
DB_USER = "weather_user"
DB_PASSWORD = "weather_pass"

today = datetime.now().date()

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": (today - timedelta(days=3)).isoformat(),
    "end_date": (today - timedelta(days=3)).isoformat(),
    "hourly": HOURLY,
    "timezone": "Europe/Paris",
	"timeformat": "unixtime",
}

response = openmeteo.weather_api(API_URL, params = params)

data = response[0].Hourly()
hourly_temperature_2m = data.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = data.Variables(1).ValuesAsNumpy()
hourly_precipitation = data.Variables(2).ValuesAsNumpy()
hourly_cloud_cover = data.Variables(3).ValuesAsNumpy()
hourly_wind_speed_10m = data.Variables(4).ValuesAsNumpy()
hourly_wind_direction_10m = data.Variables(5).ValuesAsNumpy()
hourly_soil_temperature_0_to_7cm = data.Variables(6).ValuesAsNumpy()
hourly_soil_moisture_0_to_7cm = data.Variables(7).ValuesAsNumpy()
hourly_is_day = data.Variables(8).ValuesAsNumpy()

dates = pd.date_range(
    start = pd.to_datetime(data.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(data.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = data.Interval()),
	inclusive = "left"
).tolist()

weather_rows = []

for ts, temp, hum, precipit, cloud, wind_sp, wind_dir, soil_t, soil_m, d in zip(dates, 
                                                                                hourly_temperature_2m, 
                                                                                hourly_relative_humidity_2m, 
                                                                                hourly_precipitation,
                                                                                hourly_cloud_cover,
                                                                                hourly_wind_speed_10m,
                                                                                hourly_wind_direction_10m,
                                                                                hourly_soil_temperature_0_to_7cm,
                                                                                hourly_soil_moisture_0_to_7cm,
                                                                                hourly_is_day):
    weather_rows.append((
    ts,
    round(temp.item(), 3),
    round(hum.item(), 3),
    round(precipit.item(), 3),
    round(cloud.item(), 3),
    round(wind_sp.item(), 3),
    round(wind_dir.item(), 3),
    round(soil_t.item(), 3),
    round(soil_m.item(), 3),
    d.item() == 1.0,
    CITY
))


try:
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    insert_query = """
        INSERT INTO weather_raw (timestamp, temperature, humidity, precipitation,
            cloud_cover, wind_speed, wind_direction, soil_temperature, soil_moisture, is_day, city)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp, city) DO NOTHING
    """
    
    cur.executemany(insert_query, weather_rows)

    # Valider la transaction
    conn.commit()
    print(f"{len(weather_rows)} lignes insérées dans weather_raw.")

except Exception as e:
    print("Erreur PostgreSQL :", e)

finally:
    # fermer la connexion
    if cur:
        cur.close()
    if conn:
        conn.close()
