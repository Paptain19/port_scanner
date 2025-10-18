# port-scanner

A simple concurrent TCP port scanner with a minimal Flask dashboard to centralize discovered hosts and open ports.

## Features
- Concurrent TCP scanning using `ThreadPoolExecutor`
- Optional banner grabbing for open services
- Persist discovered hosts and ports in MySQL
- Minimal Flask dashboard to view hosts
- Autonomous DB initialization script (`db_init.py`)
- Minimal Dockerfile included

---

## Requirements
- Python 3.8+
- MySQL (Community Edition or compatible like MariaDB)
- `pip` for installing Python dependencies
- (optional) Docker & docker-compose

---

## Quick install (local)

1. Clone the repositor
```bash

git clone https://github.com/Paptain19/port-scanner.git
cd port-scanner

python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set DB_HOST, DB_USER, DB_PASS, DB_DATABASE

python db_init.py
# Initialize the database

# Usage
python scanner.py target.example.com --ports 1-1024 --workers 200 --timeout 1.0

# Run the Flask dashboard
python app.py
# Open http://127.0.0.1:5000 to view the dashboard
