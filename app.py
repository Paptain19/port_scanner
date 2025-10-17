from flask import Flask, render_template
import _mysql_connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        databse=os.getenv("DB_DATABASE")
    )
    return conn

@app.route("/")
def dashboard():
    conn = get_db_connection
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT ip_address, hostname, last_seen FROM Hotes ORDERR BY last_seen DESC")
    hosts = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("dashboard.html", hosts=hosts)


if __name__ == "__main__":
    app.run(debug=True)