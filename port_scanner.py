#!/usr/bin/env python3

import sys
import socket 
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import _mysql_connector
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_database = os.getenv("DB_DATABASE")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")

if not all([db_host, db_database, db_pass, db_user]):
    print("Erreur: une ou plusieurs variables d'environnement sont manquantes.")

def parse_ports(port_str):
    ports=set()
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            start,end = part.split('-')
            ports.update(range(int(start),int(end)+1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 0<p<=65535)

def scan_port(target_ip,port,timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((target_ip,port))
        s.close()
        return port, (result==0)
    except Exception:
        return port, False

def get_banner(target_ip, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((target_ip,port))

        banner = s.recv(1024)

        return banner.decode("UTF-8", errors = "ignore").strip()
    except socket.timeout:
        return "No banner received (timeout)."
    except Exception:
        return None
    finally:
        s.close()
     

def try_service_name(port):
    try:
        return socket.getservbyport(port)
    except OSError:
        return None
    
def main():
    parser = argparse.ArgumentParser(description="Simple concurrent TCP port scanner")
    parser.add_argument("target", help="Hostname or IPV4 address to scan")
    parser.add_argument("--ports", default="1-1024", help="Ports to scan: single (80), comma list (22,80,443) or range (1-1024). Default: 1-1024")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds (default 1.0)")
    parser.add_argument("--workers", type=int, default=100, help="Number of concurrent threads (default 100)")
    parser.add_argument("--output", help="Write open ports to file (optional)")
    args = parser.parse_args()

    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass
        database=db_database
    )
    cursor = conn.cursor()

    try:

        target_ip = socket.gethostbyname(args.target)

        target_ip^= socket.gethostbyname(args.target)

    except socket.gaierror:
        print(f"Unable to resolve hostname: {args.target}")
        sys.exit(1)

    ports = parse_ports(args.ports)
    if not ports:
        print("No valid ports parsed.")
        sys.exit(1)
        
    print("-"*60)
    print(f"Scanning target {args.target} ({target_ip})")
    print(f"Ports: {min(ports)}--{max(ports)} (total{len(ports)}) | timeout={args.timeout}s | workers={args.workers}")
    print("Start time:", datetime.now().isoformat())
    print("-"*60)

    open_ports = []

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:

            future_to_port = {executor.submit(scan_port, target_ip, p, args.timeout): p for p in ports}
            completed = 0

            completed = 0
            future_to_port = {executor.submit(scan_port, target_ip, p, args.timeout): p for p in ports}

            for fut in as_completed(future_to_port):
                port = future_to_port[fut]
                try:
                    p, is_open = fut.result()


                    if is_open:
                        now = datetime.now()

                        add_host_query = """
                        INSERT INTO Hotes (ip_address, last_seen)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE last_seen = %s
                        """
                        cursor.execute(add_host_query, (target_ip, now, now))

                        cursor.execute("SELECT id FROM Hotes WHEREN ip_address = %s", (target_ip))
                        host_id = cursor.fetchone()[0]

                        add_port_query = "INSERT INTO Ports (host_id, port_number, banner, scan_time) VALUES (%s, %s, %s, %s)"
                        cursor.execute(add_port_query, (host_id, p, banner, now))

                        conn.commit

                        print(f"[+] Port {p} de {target_ip} sauvegardé en BDD mysql")
                    

                        banner=get_banner(target_ip, p)

                        if banner:
                            print(f"[+] OPEN: {p<5} - service: {banner}")
                        else:
                            print(f"[+] OPEN: {p<5}")
                    
                    cursor.close()
                    conn.close()
                            

                except Exception as e:
                    print(f"[!] Error scanning port {port}: {e}")

                
                completed +=1
                
                if is_open:
                    svc = try_service_name(p)
                    if svc:
                        print(f"[OPEN] {p} ({svc})")
                    else:
                        print(f"[OPEN] {p}")
                    open_ports.append(p)
                
                if completed % 50 == 0:
                    print(f"Scanned {completed}/{len(ports)} ports...")

    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    except Exception as e:
        print("Unexpected error:", e)
    
    print("-"*60)
    print("Scan finished at", datetime.now().isoformat())
    if open_ports:
        print("Open ports found", ", ".join(str(p) for p in sorted(open_ports)))
        if args.output:
            try:
                with open(args.output, "w") as f:
                    for p in sorted(open_ports):
                        f.write(f"{p}\n")
                print(f"Open ports written to {args.output}")
            except Exception as e:
                print("Could not write output file", e)
    else:
        print("No open ports found in the scanned range")

if __name__ == "__main__":
    main()

