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

## Security and legal
**Legal and ethical notice:** Port scanning can be considered intrusive or hostile behaviour by some network owners and may be illegal in certain jurisdictions when performed without permission. Only run this tool against systems and networks you own or where you have **explicit written authorization** to test. Always obtain prior, documented consent and follow responsible disclosure practices if you discover vulnerabilities. The author assumes no responsibility for misuse — you are fully responsible for ensuring your use complies with local laws and policies.

---

## Quick install (local)

1. Clone the repository
```bash
git clone https://github.com/Paptain19/port-scanner.git
cd port-scanner
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
```

3. Copy .env.example to .env and fill in values (DB connection etc.):
```bash
cp .env.example .env
# then edit .env and set DB_HOST, DB_USER, DB_PASS, DB_DATABASE
```
4. Initialize the database:
```bash
python db_init.py
```

5. Run the scanner and the Flask dashboard
```bash
python scanner.py target.example.com --ports 1-1024 --workers 200 --timeout 1.0
python app.py
# Open http://127.0.0.1:5000 to view the dashboard
