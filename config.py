import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_DATABASE = "chilepal_db"
MONGO_DATABASE = "chilepal_nosql"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "chilepal_user",
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": MYSQL_DATABASE
}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

SECRET_KEY = os.getenv("SECRET_KEY", "chilepal-dev-key")
