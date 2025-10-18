import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_DATABASE")
}

DB_NAME = DB_CONFIG["database"]

try:
   
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()


    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4'")
    print(f'Base de données "{DB_NAME}" vérifiée/créée avec succès.')

    conn.database = DB_NAME

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Hotes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(255) NOT NULL UNIQUE,
            hostname VARCHAR(255),
            last_seen DATETIME
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            host_id INT,
            port_number INT NOT NULL,
            banner TEXT,
            scan_time DATETIME,
            FOREIGN KEY (host_id) REFERENCES Hotes(id) ON DELETE CASCADE
        )
    """)

    print("Tables 'Hotes' et 'Ports' créées ou vérifiées avec succès.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Erreur: Mauvais nom d'utilisateur ou mot de passe")
    else:
        print("Erreur MySQL:", err)
finally:
    if "cursor" in locals():
        cursor.close()
    if "conn" in locals() and conn.is_connected():
        conn.close()
