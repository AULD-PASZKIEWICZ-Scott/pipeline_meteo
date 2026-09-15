import requests       # Pour appeler l'API météo
import psycopg2       # Pour se connecter à PostgreSQL
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
API_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = 43.61       # Exemple : Montpellier
LONGITUDE = 3.87
HOURLY = "temperature_2m"
CITY = "Montpellier"

DB_HOST = "weather_postgres"
DB_PORT = 5432
DB_NAME = "weather_db"
DB_USER = "weather_user"
DB_PASSWORD = "weather_pass"

# -------------------------------
# 1️⃣ Récupérer les données depuis l'API
# -------------------------------
params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": HOURLY,
    "past_hours": 36,
}

# Appel de l'API
response = requests.get(API_URL, params=params)

# Vérifier que la requête a fonctionné
if response.status_code != 200:
    raise Exception(f"Erreur API : {response.status_code}")

data = response.json()

# Les données horaires sont dans data['hourly']['temperature_2m'] et data['hourly']['time']
temperatures = data['hourly'][HOURLY]
timestamps = data['hourly']['time']

# -------------------------------
# 2️⃣ Préparer les données pour PostgreSQL
# -------------------------------
# On va créer une liste de tuples : [(timestamp1, temp1, city), ...]
weather_rows = []

for ts, temp in zip(timestamps, temperatures):
    # Convertir le timestamp en objet datetime
    dt = datetime.fromisoformat(ts)
    weather_rows.append((dt, temp, CITY))

# -------------------------------
# 3️⃣ Insérer les données dans PostgreSQL
# -------------------------------
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

    # On insère toutes les lignes avec une seule commande executemany
    insert_query = """
        INSERT INTO weather_raw (timestamp, temperature, city)
        VALUES (%s, %s, %s)
        ON CONFLICT (timestamp, city) DO NOTHING
    """
    cur.executemany(insert_query, weather_rows)

    # Valider la transaction
    conn.commit()
    print(f"{len(weather_rows)} lignes insérées dans weather_raw.")

except Exception as e:
    print("Erreur PostgreSQL :", e)

finally:
    # Toujours fermer la connexion
    if cur:
        cur.close()
    if conn:
        conn.close()
