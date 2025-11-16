import os
import time
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection(retries=5, delay=5):
    """
    Connect to MySQL with retry mechanism.
    Returns a connection or None if all attempts fail.
    """
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root"),
                database=os.getenv("DB_NAME", "coffee_management_system")
            )
            print("✅ Connected to database")
            return conn
        except mysql.connector.Error as e:
            print(f"❌ Attempt {attempt}/{retries} failed: {e}")
            time.sleep(delay)
    print("❌ Could not connect to the database after multiple attempts.")
    return None
