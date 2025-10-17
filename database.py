import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "user": "tdivanach",
    "password": "SQL&Paddi29200@",
    "host": "127.0.0.1",
    "database": "network_monitor_db"
}



try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()


    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Hotes (
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   ip_address VARCHAR(255) NOT NULL UNIQUE?
                   hostname VARCHAR(255),
                   last_seen DATETIME
                    )
                """)
    

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Ports(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   host_id INT,
                   port_number INT NOT NULL,
                   banner TEXT,
                   scan_time DATETIME,
                   FOREIGN KEY (host_id) REFERENCES Hotes (id) ON DELETE CASCADE
                    )
                """)
    
    print(f"Base de données " {DB_CONFIG["database"]} " et tables vérifiées/créées avec succés.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Erreur: Mauvais nom d'utilisateur ou mot de passe")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print(f"Erreur: La base de données " {DB_CONFIG["database"]} " n'existe pas")
    else:
        print(err)
finally:
    if "conn" in locals() and conn.is_connected():
        cursor.close()
        conn.close()