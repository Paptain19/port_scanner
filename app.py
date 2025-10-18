from flask import Flask, render_template
import mysql.connector  
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_DATABASE")  
        )
        return conn
    except mysql.connector.Error as e:
        print(f"[!] Erreur de connexion MySQL : {e}")
        return None

@app.route("/")
def dashboard():
    conn = get_db_connection() 
    if conn is None:
        return "Erreur : impossible de se connecter à la base de données.", 500

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ip_address, hostname, last_seen FROM Hotes ORDER BY last_seen DESC")  # ✅ correction "ORDERR"
        hosts = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"[!] Erreur SQL : {e}")
        hosts = []
    finally:
        cursor.close()
        conn.close()

  
    return render_template("dashboard.html", hosts=hosts)

if __name__ == "__main__":
    app.run(debug=True)
