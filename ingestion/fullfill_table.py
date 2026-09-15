import requests
import psycopg2
from datetime import datetime
from dateutil.relativedelta import relativedelta


API_URL = "https://archive-api.open-meteo.com/v1/archive"

LATITUDE = 43.61
LONGITUDE = 3.87
HOURLY = "temperature_2m"
CITY = "Montpellier"

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "weather_db"
DB_USER = "weather_user"
DB_PASSWORD = "weather_pass"


# Dates : 4 derniers mois
end_date = datetime.now().date()
start_date = end_date - relativedelta(months=4)

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": start_date,
    "end_date": end_date,
    "hourly": HOURLY,
    "timezone": "Europe/Paris"
}


# Appel API
response = requests.get(API_URL, params=params)

if response.status_code != 200:
    raise Exception(f"Erreur API : {response.status_code}")

data = response.json()

temperatures = data["hourly"][HOURLY]
timestamps = data["hourly"]["time"]


# Préparation des données
weather_rows = []

for ts, temp in zip(timestamps, temperatures):
    dt = datetime.fromisoformat(ts)
    weather_rows.append((dt, temp, CITY))


# Connexion PostgreSQL
conn = None
cur = None

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor()

    insert_query = """
        INSERT INTO weather_raw (timestamp, temperature, city)
        VALUES (%s, %s, %s)
    """

    cur.executemany(insert_query, weather_rows)

    conn.commit()

    print(f"{len(weather_rows)} lignes insérées dans weather_raw.")

except Exception as e:
    print("Erreur PostgreSQL :", e)

finally:
    if cur:
        cur.close()

    if conn:
        conn.close()