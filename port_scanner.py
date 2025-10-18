#!/usr/bin/env python3

import sys
import socket
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_database = os.getenv("DB_DATABASE")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")

if not all([db_host, db_database, db_user, db_pass]):
    print("Erreur: une ou plusieurs variables d'environnement sont manquantes.")


def parse_ports(port_str):
    ports = set()
    for part in port_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            try:
                s = int(start)
                e = int(end)
            except ValueError:
                continue
            ports.update(range(s, e + 1))
        else:
            try:
                ports.add(int(part))
            except ValueError:
                continue
    return sorted(p for p in ports if 0 < p <= 65535)

def scan_port(target_ip, port, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((target_ip, port))
        s.close()
        return port, (result == 0)
    except Exception:
        return port, False

def get_banner(target_ip, port, timeout=2):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
   
        s.connect((target_ip, port))
        try:
            banner = s.recv(1024)
            return banner.decode("utf-8", errors="ignore").strip()
        except socket.timeout:
            return "No banner received (timeout)."
        except Exception:
            return None
    except Exception:
        return None
    finally:
        if s:
            s.close()

def try_service_name(port):
    try:
        return socket.getservbyport(port, "tcp")
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


    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_database
        )
        cursor = conn.cursor()
    except Exception as e:
        print("Impossible de se connecter à la base de données :", e)
  
        cursor = None
        conn = None

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"Unable to resolve hostname: {args.target}")
        sys.exit(1)

    ports = parse_ports(args.ports)
    if not ports:
        print("No valid ports parsed.")
        sys.exit(1)

    print("-" * 60)
    print(f"Scanning target {args.target} ({target_ip})")
    print(f"Ports: {min(ports)}--{max(ports)} (total {len(ports)}) | timeout={args.timeout}s | workers={args.workers}")
    print("Start time:", datetime.now().isoformat())
    print("-" * 60)

    open_ports = []
    completed = 0

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_port = {executor.submit(scan_port, target_ip, p, args.timeout): p for p in ports}

            for fut in as_completed(future_to_port):
                port = future_to_port[fut]
                try:
                    p, is_open = fut.result()
                except Exception as e:
                    print(f"[!] Error scanning port {port}: {e}")
                    completed += 1
                    continue

                if is_open:
                    now = datetime.now()
               
                    banner = get_banner(target_ip, p)

                    if cursor and conn:
                        try:
                            add_host_query = """
                                INSERT INTO Hotes (ip_address, last_seen)
                                VALUES (%s, %s)
                                ON DUPLICATE KEY UPDATE last_seen = %s
                            """
                            cursor.execute(add_host_query, (target_ip, now, now))
                            conn.commit()

                
                            cursor.execute("SELECT id FROM Hotes WHERE ip_address = %s", (target_ip,))
                            row = cursor.fetchone()
                            host_id = row[0] if row else None

                            if host_id is not None:
                                add_port_query = "INSERT INTO Ports (host_id, port_number, banner, scan_time) VALUES (%s, %s, %s, %s)"
                                cursor.execute(add_port_query, (host_id, p, banner, now))
                                conn.commit()
                                print(f"[+] Port {p} de {target_ip} sauvegardé en BDD mysql")
                        except Exception as db_e:
                            print(f"[!] DB error for port {p}: {db_e}")

             
                    svc = try_service_name(p)
                    if banner:
                        print(f"[OPEN] {p} - banner: {banner}")
                    elif svc:
                        print(f"[OPEN] {p} ({svc})")
                    else:
                        print(f"[OPEN] {p}")

                    open_ports.append(p)

        
                completed += 1
                if completed % 50 == 0 or completed == len(ports):
                    print(f"Scanned {completed}/{len(ports)} ports...")

    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    print("-" * 60)
    print("Scan finished at", datetime.now().isoformat())
    if open_ports:
        print("Open ports found:", ", ".join(str(p) for p in sorted(open_ports)))
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

