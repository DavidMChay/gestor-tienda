from sqlalchemy import create_engine
import os

user = "postgres.tidxgrbtrrqbuxnkmwji"
password = "ZorroPuto69!"
host = "aws-0-us-west-1.pooler.supabase.com"
port = "6543"
dbname = "postgres"

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Conexión exitosa a la base de datos")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
